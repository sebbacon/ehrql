import os

import hypothesis as hyp
import hypothesis.strategies as st
import pytest

from databuilder.query_model.nodes import (
    AggregateByPatient,
    Case,
    Column,
    Function,
    TableSchema,
    count_nodes,
    node_types,
)

from ..conftest import QUERY_ENGINE_NAMES, engine_factory
from ..lib.query_model_utils import get_all_operations
from . import data_setup, data_strategies, variable_strategies

# To simplify data generation, all tables have the same schema.
schema = TableSchema(i1=Column(int), i2=Column(int), b1=Column(bool), b2=Column(bool))
(
    patient_classes,
    event_classes,
    all_patients_query,
    sqla_metadata,
) = data_setup.setup(schema, num_patient_tables=2, num_event_tables=2)

# Use the same strategies for values both for query generation and data generation.
int_values = st.integers(min_value=0, max_value=10)
bool_values = st.booleans()


variable_strategy = variable_strategies.variable(
    [c.__tablename__ for c in patient_classes],
    [c.__tablename__ for c in event_classes],
    schema,
    int_values,
    bool_values,
)
data_strategy = data_strategies.data(
    patient_classes, event_classes, schema, int_values, bool_values
)
settings = dict(
    max_examples=(int(os.environ.get("GENTEST_EXAMPLES", 100))),
    deadline=None,
    suppress_health_check=[hyp.HealthCheck.filter_too_much, hyp.HealthCheck.too_slow],
)


@pytest.fixture(scope="session")
def query_engines(request):
    # By contrast with the `engine` fixture which is parametrized over the types of
    # engine and so returns them one at a time, this fixture constructs and returns all
    # the engines together at once
    return {
        name: engine_factory(request, name)
        for name in QUERY_ENGINE_NAMES
        # The Spark engine is still too slow to run generative tests against
        if name != "spark"
    }


class ObservedInputs:
    _inputs = set()

    def record(self, variable, data):
        hashable_data = frozenset(self._hashable(item) for item in data)
        self._inputs.add((variable, hashable_data))

    @property
    def variables(self):  # pragma: no cover
        return {i[0] for i in self._inputs}

    @property
    def records(self):  # pragma: no cover
        return {i[1] for i in self._inputs}

    @property
    def unique_inputs(self):  # pragma: no cover
        return self._inputs

    @staticmethod
    def _hashable(item):
        copy = item.copy()

        # SQLAlchemy ORM objects aren't hashable, but the name is good enough for us
        copy["type"] = copy["type"].__name__

        # There are only a small number of values in each record and their order is predictable,
        # so we can record just the values as a tuple and recover the field names later
        # if we want them.
        return tuple(copy.values())


observed_inputs = ObservedInputs()


@pytest.fixture(scope="session")
def recorder():  # pragma: no cover
    yield observed_inputs.record

    if not os.getenv("GENTEST_COMPREHENSIVE"):
        return

    all_operations = set(get_all_operations())
    known_missing = {
        AggregateByPatient.CombineAsSet,
        Case,
        Function.In,
        Function.StringContains,
        Function.CastToFloat,
        Function.CastToInt,
        Function.DateAddYears,
        Function.DateAddMonths,
        Function.DateAddDays,
        Function.YearFromDate,
        Function.MonthFromDate,
        Function.DayFromDate,
        Function.DateDifferenceInYears,
        Function.DateDifferenceInMonths,
        Function.DateDifferenceInDays,
        Function.ToFirstOfYear,
        Function.ToFirstOfMonth,
    }

    operations_seen = {o for v in observed_inputs.variables for o in node_types(v)}

    unexpected_missing = all_operations - known_missing - operations_seen
    assert (
        not unexpected_missing
    ), f"unseen operations: {[o.__name__ for o in unexpected_missing]}"

    unexpected_present = known_missing & operations_seen
    assert (
        not unexpected_present
    ), f"unexpectedly seen operations: {[o.__name__ for o in unexpected_present]}"


@hyp.given(variable=variable_strategy, data=data_strategy)
@hyp.settings(**settings)
def test_query_model(query_engines, variable, data, recorder):
    recorder(variable, data)
    tune_inputs(variable)
    run_test(query_engines, data, variable)


def tune_inputs(variable):
    # Encourage Hypothesis to maximize the number and type of nodes
    hyp.target(count_nodes(variable), label="number of nodes")
    hyp.target(len(node_types(variable)), label="number of node types")


def run_test(query_engines, data, variable):
    instances = instantiate(data)
    variables = {
        "population": all_patients_query,
        "v": variable,
    }

    results = [
        (name, run_with(engine, instances, variables))
        for name, engine in query_engines.items()
    ]

    first_name, first_results = results[0]
    for other_name, other_results in results[1:]:
        assert (
            first_results == other_results
        ), f"Mismatch between {first_name} and {other_name}"


def run_with(engine, instances, variables):
    engine.setup(instances, metadata=sqla_metadata)
    return engine.extract_qm(variables)


def instantiate(data):
    instances = []
    for item in data:
        item = item.copy()
        instances.append(item.pop("type")(**item))
    return instances

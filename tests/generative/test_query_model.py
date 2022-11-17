import os

import hypothesis as hyp
import hypothesis.strategies as st
import pytest

from databuilder.query_model.nodes import Column, TableSchema

from ..conftest import QUERY_ENGINE_NAMES, engine_factory
from . import data_setup, data_strategies, variable_strategies
from .conftest import count_nodes, observe_inputs

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
    max_examples=(int(os.environ.get("EXAMPLES", 100))),
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


@hyp.given(variable=variable_strategy, data=data_strategy)
@hyp.settings(**settings)
def test_query_model(query_engines, variable, data):
    tune_inputs(variable)
    observe_inputs(variable, data)
    run_test(query_engines, data, variable)


def tune_inputs(variable):
    # Hypothesis maximizes the metric, which makes the number of nodes in the variable
    # tend towards the target. The target chosen here seems to give a reasonable spread
    # of query model graphs
    target_size = 40
    metric = -abs(target_size - count_nodes(variable))
    hyp.target(metric)


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

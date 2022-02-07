from types import SimpleNamespace

import pytest

from databuilder.query_model import (
    AggregateByPatient,
    DomainMismatchError,
    Filter,
    Function,
    OneRowPerPatientFrame,
    OneRowPerPatientSeries,
    PickOneRowPerPatient,
    Position,
    SelectColumn,
    SelectTable,
    Sort,
    Value,
)


@pytest.fixture
def queries():
    q = SimpleNamespace()
    events = SelectTable("events")
    code = SelectColumn(events, "code")
    date = SelectColumn(events, "date")
    vaccinations = Filter(events, Function.EQ(code, Value("abc123")))
    q.has_vaccination = AggregateByPatient.Exists(
        SelectColumn(vaccinations, "patient_id")
    )
    q.first_vaccination = PickOneRowPerPatient(Sort(vaccinations, date), Position.FIRST)
    return q


def test_queries_have_expected_types(queries):
    assert isinstance(queries.has_vaccination, OneRowPerPatientSeries)
    assert isinstance(queries.first_vaccination, OneRowPerPatientFrame)


def test_queries_are_hashable(queries):
    for query in vars(queries).values():
        assert hash(query) is not None


# We don't _have_ to maintain this property, but it's quite a convenient one to have and
# if we're going to break it then let's at least do so deliberately
def test_query_reprs_round_trip(queries):
    # This relies on all public query model names being imported into local scope
    for query in vars(queries).values():
        assert eval(repr(query)) == query


def test_mixing_domains_throws_error():
    events = SelectTable("events")
    vaccinations = SelectTable("vaccinations")
    vaccine_code = SelectColumn(vaccinations, "code")
    with pytest.raises(DomainMismatchError):
        Filter(events, Function.EQ(vaccine_code, Value("abc123")))

import dataclasses
import datetime
import functools
import re
from collections import ChainMap
from pathlib import Path

from ehrql.codes import BaseCode
from ehrql.file_formats import read_dataset
from ehrql.query_model import nodes as qm
from ehrql.query_model.column_specs import get_column_specs_from_schema
from ehrql.query_model.nodes import get_series_type, has_one_row_per_patient
from ehrql.query_model.population_validation import validate_population_definition
from ehrql.utils import date_utils
from ehrql.utils.docs_utils import exclude_from_docs
from ehrql.utils.string_utils import strip_indent


VALID_VARIABLE_NAME_RE = re.compile(r"^[A-Za-z]+[A-Za-z0-9_]*$")

# This gets populated by the `__init_subclass__` methods of EventSeries and
# PatientSeries. Its structure is:
#
#   (<type>, <is_patient_level>): <SeriesClass>
#
# For example:
#
#   (bool, False): BoolEventSeries,
#   (bool, True): BoolPatientSeries,
#
REGISTERED_TYPES = {}


@dataclasses.dataclass
class DummyDataConfig:
    population_size: int = 500


# Because ehrQL classes override `__eq__` we can't use them as dictionary keys. So where
# the query model expects dicts we represent them as lists of pairs, which the
# `_apply()` function can convert to dicts when it passes them to the query model.
class _DictArg(list):
    "Internal class for passing around dictionary arguments"


class Dataset:
    """
    Create a dataset with [`create_dataset`](#create_dataset).
    """

    def __init__(self):
        # Set attributes with `object.__setattr__` to avoid using the
        # `__setattr__` method on this class, which prohibits use of these
        # attribute names
        object.__setattr__(self, "variables", {})
        object.__setattr__(self, "dummy_data_config", DummyDataConfig())

    def define_population(self, population_condition):
        """
        Define the condition that patients must meet to be included in the Dataset, in
        the form of a [boolean patient series](#BoolPatientSeries) e.g.
        ```py
        dataset.define_population(patients.date_of_birth < "1990-01-01")
        ```
        """
        validate_population_definition(population_condition._qm_node)
        self.variables["population"] = population_condition

    def configure_dummy_data(self, *, population_size):
        """
        Configure the dummy data to be generated.

        ```py
        dataset.configure_dummy_data(population_size=10000)
        ```
        """
        self.dummy_data_config.population_size = population_size

    @exclude_from_docs
    def configure_dummy_dataset(self, **kwargs):  # pragma: no cover
        """
        Deprecated alias from `configure_dummy_data`
        """
        return self.configure_dummy_data(**kwargs)

    def __setattr__(self, name, value):
        if name == "population":
            raise AttributeError(
                "Cannot set variable 'population'; use define_population() instead"
            )
        if name in self.variables:
            raise AttributeError(f"'{name}' is already set and cannot be reassigned")
        if name in ("patient_id", "variables", "dummy_data_config"):
            raise AttributeError(f"'{name}' is not an allowed variable name")
        if not VALID_VARIABLE_NAME_RE.match(name):
            raise AttributeError(
                f"Variable names must start with a letter, and contain only "
                f"alphanumeric characters and underscores (you defined a "
                f"variable '{name}')"
            )
        if not isinstance(value, BaseSeries):
            raise TypeError(
                f"Invalid variable '{name}'. Dataset variables must be values not whole rows"
            )
        if not qm.has_one_row_per_patient(value._qm_node):
            raise TypeError(
                f"Invalid variable '{name}'. Dataset variables must return one row per patient"
            )
        self.variables[name] = value

    def __getattr__(self, name):
        if name in self.variables:
            return self.variables[name]
        raise AttributeError(f"Variable '{name}' has not been defined")


def create_dataset():
    """
    A dataset defines the patients you want to include in your population and the
    variables you want to extract for them.

    A dataset definition file must define a dataset called `dataset`:

    ```py
    dataset = create_dataset()
    ```

    Add variables to the dataset as attributes:

    ```py
    dataset.age = patients.age_on("2020-01-01")
    ```
    """
    return Dataset()


def compile(dataset):  # noqa A003
    return {k: v._qm_node for k, v in dataset.variables.items()}


# BASIC SERIES TYPES
#


@dataclasses.dataclass(frozen=True)
class BaseSeries:
    _qm_node: qm.Node

    def __hash__(self):
        # The issue here is not mutability but the fact that we overload `__eq__` for
        # syntatic sugar, which makes these types spectacularly ill-behaved as dict keys
        raise TypeError(f"unhashable type: {self.__class__.__name__!r}")

    def __bool__(self):
        raise TypeError(
            "The keywords 'and', 'or', and 'not' cannot be used with ehrQL, please "
            "use the operators '&', '|' and '~' instead.\n"
            "(You will also see this error if you try use a chained comparison, "
            "such as 'a < b < c'.)"
        )

    @staticmethod
    def _cast(value):
        # Series have the opportunity to cast arguments to their methods e.g. to convert
        # ISO date strings to date objects. By default, this is a no-op.
        return value

    # These are the basic operations that apply to any series regardless of type or
    # dimension
    def __eq__(self, other):
        """
        Return a boolean series comparing each value in this series with its
        corresponding value in `other`.

        Note that the result of comparing anything with NULL (including NULL itself) is NULL.
        """
        other = self._cast(other)
        return _apply(qm.Function.EQ, self, other)

    def __ne__(self, other):
        """
        Return the inverse of `==` above.

        Note that the same point regarding NULL applies here.
        """
        other = self._cast(other)
        return _apply(qm.Function.NE, self, other)

    def is_null(self):
        """
        Return a boolean series which is True for each value in this series which is
        NULL, and False otherwise.
        """
        return _apply(qm.Function.IsNull, self)

    def is_not_null(self):
        """
        Return the inverse of `is_null()` above.
        """
        return self.is_null().__invert__()

    def if_null_then(self, other):
        """
        Replace any NULL value in this series with the corresponding value in `other`.

        Note that `other` must be of the same type as this series.
        """
        return case(
            when(self.is_not_null()).then(self),
            default=self._cast(other),
        )

    def is_in(self, other):
        """
        Return a boolean series which is True for each value in this series which is
        contained in `other`, where `other` can be any of the standard "container"
        types: tuple, list, set, frozenset, or dict.
        """
        # For iterable arguments, apply any necessary casting and convert to the
        # immutable Set type required by the query model. We don't accept arbitrary
        # iterables here because too many types in Python are iterable and there's the
        # potential for confusion amongst the less experienced of our users.
        if isinstance(other, tuple | list | set | frozenset | dict):
            other = frozenset(map(self._cast, other))
        return _apply(qm.Function.In, self, other)

    def is_not_in(self, other):
        """
        Return the inverse of `is_in()` above.
        """
        return self.is_in(other).__invert__()

    def map_values(self, mapping, default=None):
        """
        Accepts a dictionary mapping one set of values to another and applies that
        mapping to the series e.g.

        ```py
        status = status_code.map_values(
            {1: "pending", 2: "accepted", 3: "completed"},
            default="unknown"
        )
        ```
        """
        return case(
            *[
                when(self == from_value).then(to_value)
                for from_value, to_value in mapping.items()
            ],
            default=default,
        )


class PatientSeries(BaseSeries):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register the series using its `_type` attribute
        REGISTERED_TYPES[cls._type, True] = cls


class EventSeries(BaseSeries):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register the series using its `_type` attribute
        REGISTERED_TYPES[cls._type, False] = cls

    def count_distinct_for_patient(self):
        """
        Return a integer patient series counting the number of distinct values for each
        patient in the series (ignoring any NULL values). Not that if a patient has no
        values at all in the series the result will be zero rather than NULL.
        """
        return _apply(qm.AggregateByPatient.CountDistinct, self)


# BOOLEAN SERIES
#


class BoolFunctions:
    def __and__(self, other):
        """
        Logical AND

        Return a boolean series which is True where both this series and `other` are
        True, False where either are False, and NULL otherwise.
        """
        other = self._cast(other)
        return _apply(qm.Function.And, self, other)

    def __or__(self, other):
        """
        Logical OR

        Return a boolean series which is True where either this series or `other` is
        True, False where both are False, and NULL otherwise.
        """
        other = self._cast(other)
        return _apply(qm.Function.Or, self, other)

    def __invert__(self):
        """
        Logical NOT

        Return a boolean series which is the inverse of this series i.e. where True
        becomes False, False becomes True, and NULL stays as NULL.
        """
        return _apply(qm.Function.Not, self)


class BoolPatientSeries(BoolFunctions, PatientSeries):
    _type = bool


class BoolEventSeries(BoolFunctions, EventSeries):
    _type = bool


# METHODS COMMON TO ALL COMPARABLE TYPES
#


class ComparableFunctions:
    def __lt__(self, other):
        """
        Return a boolean series which is True for each value in this series that is
        strictly less than its corresponding value in `other` and False otherwise (or NULL
        if either value is NULL).
        """
        other = self._cast(other)
        return _apply(qm.Function.LT, self, other)

    def __le__(self, other):
        """
        Return a boolean series which is True for each value in this series that is less
        than or equal to its corresponding value in `other` and False otherwise (or NULL
        if either value is NULL).
        """
        other = self._cast(other)
        return _apply(qm.Function.LE, self, other)

    def __ge__(self, other):
        """
        Return a boolean series which is True for each value in this series that is
        greater than or equal to its corresponding value in `other` and False otherwise
        (or NULL if either value is NULL).
        """
        other = self._cast(other)
        return _apply(qm.Function.GE, self, other)

    def __gt__(self, other):
        """
        Return a boolean series which is True for each value in this series that is
        strictly greater than its corresponding value in `other` and False otherwise (or
        NULL if either value is NULL).
        """
        other = self._cast(other)
        return _apply(qm.Function.GT, self, other)


class ComparableAggregations:
    def minimum_for_patient(self):
        """
        Return the minimum value in the series for each patient (or NULL if the patient
        has no values).
        """
        return _apply(qm.AggregateByPatient.Min, self)

    def maximum_for_patient(self):
        """
        Return the maximum value in the series for each patient (or NULL if the patient
        has no values).
        """
        return _apply(qm.AggregateByPatient.Max, self)


# STRING SERIES
#


class StrFunctions(ComparableFunctions):
    def contains(self, other):
        """
        Return a boolean series which is True for each string in this series which
        contains the corresponding value in `other` as a sub-string and False otherwise (or
        NULL if either value is NULL).
        """
        other = self._cast(other)
        return _apply(qm.Function.StringContains, self, other)


class StrAggregations(ComparableAggregations):
    "Empty for now"


class StrPatientSeries(StrFunctions, PatientSeries):
    _type = str


class StrEventSeries(StrFunctions, StrAggregations, EventSeries):
    _type = str


# NUMERIC SERIES
#


class NumericFunctions(ComparableFunctions):
    def __add__(self, other):
        """
        Return the sum of each corresponding value in this series and `other` (or NULL
        if either is NULL).
        """
        other = self._cast(other)
        return _apply(qm.Function.Add, self, other)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        """
        Return each value in this series with its corresponding value in `other`
        subtracted (or NULL if either is NULL).
        """
        other = self._cast(other)
        return _apply(qm.Function.Subtract, self, other)

    def __rsub__(self, other):
        return other + -self

    def __mul__(self, other):
        """
        Return the product of each corresponding value in this series and `other` (or
        NULL if either is NULL).
        """
        other = self._cast(other)
        return _apply(qm.Function.Multiply, self, other)

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        """
        Return a series with each value in this series divided by its correponding value
        in `other` (or NULL if either is NULL).

        Note that the result is always if a float even if the inputs are integers.
        """
        other = self._cast(other)
        return _apply(qm.Function.TrueDivide, self, other)

    def __rtruediv__(self, other):
        return self / other

    def __floordiv__(self, other):
        """
        Return a series with each value in this series divided by its correponding value
        in `other` and then rounded **down** to the nearest integer value (or NULL if either
        is NULL).

        Note that the result is always if an integer even if the inputs are floats.
        """
        other = self._cast(other)
        return _apply(qm.Function.FloorDivide, self, other)

    def __rfloordiv__(self, other):
        return self // other

    def __neg__(self):
        """
        Return the negation of each value in this series.
        """
        return _apply(qm.Function.Negate, self)

    def as_int(self):
        """
        Return each value in this series rounded down to the nearest integer.
        """
        return _apply(qm.Function.CastToInt, self)

    def as_float(self):
        """
        Return each value in this series as a float e.g 10 becomes 10.0
        """
        return _apply(qm.Function.CastToFloat, self)


class NumericAggregations(ComparableAggregations):
    def sum_for_patient(self):
        """
        Return the sum of all values in the series for each patient.
        """
        return _apply(qm.AggregateByPatient.Sum, self)

    def mean_for_patient(self):
        """
        Return the arithmetic mean of any non-NULL values in the series for each
        patient.
        """
        return _apply(qm.AggregateByPatient.Mean, self)


class IntPatientSeries(NumericFunctions, PatientSeries):
    _type = int


class IntEventSeries(NumericFunctions, NumericAggregations, EventSeries):
    _type = int


class FloatFunctions(NumericFunctions):
    @staticmethod
    def _cast(value):
        """
        Casting int literals to floats. We dont support casting to float for IntSeries.
        """
        if isinstance(value, int):
            return float(value)
        return value


class FloatPatientSeries(FloatFunctions, PatientSeries):
    _type = float


class FloatEventSeries(FloatFunctions, NumericAggregations, EventSeries):
    _type = float


# DATE SERIES
#


def parse_date_if_str(value):
    if isinstance(value, str):
        try:
            return datetime.date.fromisoformat(value)
        except ValueError as e:
            raise ValueError(f"{e} in {value!r}")
    else:
        return value


def cast_all_arguments(args):
    series_args = [arg for arg in args if isinstance(arg, BaseSeries)]
    if series_args:
        # Choose the first series arbitrarily, the type checker will enforce that they
        # are all the same type in any case
        cast = series_args[0]._cast
        return tuple(map(cast, args))
    else:
        # This would only be the case if all the arguments were literals, which would be
        # an unusual and pointless bit of ehrQL, but we should handle it without error
        return args


class DateFunctions(ComparableFunctions):
    @staticmethod
    def _cast(value):
        return parse_date_if_str(value)

    @property
    def year(self):
        """
        Return an integer series giving the year of each date in this series.
        """
        return _apply(qm.Function.YearFromDate, self)

    @property
    def month(self):
        """
        Return an integer series giving the month (1-12) of each date in this series.
        """
        return _apply(qm.Function.MonthFromDate, self)

    @property
    def day(self):
        """
        Return an integer series giving the day of the month (1-31) of each date in this
        series.
        """
        return _apply(qm.Function.DayFromDate, self)

    def to_first_of_year(self):
        """
        Return a date series with each date in this series replaced by the date of the
        first day in its corresponding calendar year.
        """
        return _apply(qm.Function.ToFirstOfYear, self)

    def to_first_of_month(self):
        """
        Return a date series with each date in this series replaced by the date of the
        first day in its corresponding calendar month.
        """
        return _apply(qm.Function.ToFirstOfMonth, self)

    def is_before(self, other):
        """
        Return a boolean series which is True for each date in this series that is
        earlier than its corresponding date in `other` and False otherwise (or NULL if
        either value is NULL).
        """
        return self.__lt__(other)

    def is_on_or_before(self, other):
        """
        Return a boolean series which is True for each date in this series that is
        earlier than or the same as its corresponding value in `other` and False
        otherwise (or NULL if either value is NULL).
        """
        return self.__le__(other)

    def is_after(self, other):
        """
        Return a boolean series which is True for each date in this series that is later
        than its corresponding date in `other` and False otherwise (or NULL if either value
        is NULL).
        """
        return self.__gt__(other)

    def is_on_or_after(self, other):
        """
        Return a boolean series which is True for each date in this series that is later
        than or the same as its corresponding value in `other` and False otherwise (or
        NULL if either value is NULL).
        """
        return self.__ge__(other)

    def is_between_but_not_on(self, start, end):
        """
        Return a boolean series which is True for each date in this series which is
        strictly between (i.e. not equal to) the corresponding dates in `start` and `end`.
        """
        return (self > start) & (self < end)

    def is_on_or_between(self, start, end):
        """
        Return a boolean series which is True for each date in this series which is
        between or the same as the corresponding dates in `start` and `end`.
        """
        return (self >= start) & (self <= end)

    def is_during(self, interval):
        """
        The same as `is_on_or_between()` above, but allows supplying a start/end date
        pair as single argument.
        """
        start, end = interval
        return self.is_on_or_between(start, end)

    def __sub__(self, other):
        """
        Return a series giving the difference between each date in this series and
        `other` (see [`DateDifference`](#DateDifference)).
        """
        other = self._cast(other)
        if isinstance(other, datetime.date | DateEventSeries | DatePatientSeries):
            return DateDifference(self, other)
        else:
            return NotImplemented

    def __rsub__(self, other):
        other = self._cast(other)
        if isinstance(other, datetime.date | DateEventSeries | DatePatientSeries):
            return DateDifference(other, self)
        else:
            return NotImplemented


class DateAggregations(ComparableAggregations):
    "Empty for now"


class DatePatientSeries(DateFunctions, PatientSeries):
    _type = datetime.date


class DateEventSeries(DateFunctions, DateAggregations, EventSeries):
    _type = datetime.date


# The default dataclass equality method doesn't work here and while we could define our
# own it wouldn't be very useful for this type
@dataclasses.dataclass(eq=False)
class DateDifference:
    """
    Represents the difference between two date series (i.e. it is what you get when you
    subtract one date series from another)
    """

    lhs: datetime.date | DateEventSeries | DatePatientSeries
    rhs: datetime.date | DateEventSeries | DatePatientSeries

    @property
    def days(self):
        """
        The value of the date difference in days (can be positive or negative)
        """
        return _apply(qm.Function.DateDifferenceInDays, self.lhs, self.rhs)

    @property
    def weeks(self):
        """
        The value of the date difference in whole weeks (can be positive or negative)
        """
        return self.days // 7

    @property
    def months(self):
        """
        The value of the date difference in whole calendar months (can be positive or
        negative)
        """
        return _apply(qm.Function.DateDifferenceInMonths, self.lhs, self.rhs)

    @property
    def years(self):
        """
        The value of the date difference in whole calendar years (can be positive or
        negative)
        """
        return _apply(qm.Function.DateDifferenceInYears, self.lhs, self.rhs)


@dataclasses.dataclass
class Duration:
    value: int | IntEventSeries | IntPatientSeries

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        assert cls._date_add_static is not None
        assert cls._date_add_qm is not None

    # The default dataclass equality/inequality methods don't behave correctly here
    def __eq__(self, other):
        """
        Return a boolean indicating whether the two durations have the same value and units.
        """
        if other.__class__ is not self.__class__:
            return False
        return self.value == other.value

    def __ne__(self, other):
        """
        Return a boolean indicating whether the two durations do not have the same value
        and units.
        """
        # We have to apply different inversion logic depending on whether we have a
        # boolean or a BoolSeries
        is_equal = self == other
        if isinstance(is_equal, bool):
            return not is_equal
        else:
            return is_equal.__invert__()

    def __add__(self, other):
        """
        Add this duration to a date to produce a new date.

        Alternatively two durations with the same units may be added to produce a new duration.
        """
        other = parse_date_if_str(other)
        if isinstance(self.value, int) and isinstance(other, datetime.date):
            # If both operands are static values we can perform the date arithmetic
            # directly ourselves
            return self._date_add_static(other, self.value)
        elif isinstance(other, datetime.date | DateEventSeries | DatePatientSeries):
            # Otherwise we create the appropriate query model construct
            return _apply(self._date_add_qm, other, self.value)
        elif isinstance(other, self.__class__):
            # Durations of the same type can be added together
            return self.__class__(self.value + other.value)
        else:
            # Nothing else is handled
            return NotImplemented

    def __sub__(self, other):
        """
        Subtract another duration of the same units from this duration.
        """
        return self.__add__(other.__neg__())

    def __radd__(self, other):
        return self.__add__(other)

    def __rsub__(self, other):
        return self.__neg__().__add__(other)

    def __neg__(self):
        """
        Invert this duration so that rather that representing a movement, say, four
        weeks forwards in time it now represents a movement four weeks backwards.
        """
        return self.__class__(self.value.__neg__())

    def starting_on(self, date):
        """
        Return a list of time intervals covering the duration starting on the supplied
        date. For example:
        ```py
        weeks(3).starting_on("2000-01-01")
        ```
        Returns:
        ```
        [
            (date(2000, 1, 1), date(2000, 1, 7)),
            (date(2000, 1, 8), date(2000, 1, 14)),
            (date(2000, 1, 15), date(2000, 1, 21)),
        ]
        ```

        Useful for generating the `intervals` arguments to [`Measures`](#Measures).
        """
        return self._generate_intervals(date, self.value, 1, "starting_on")

    def ending_on(self, date):
        """
        Return a list of time intervals covering the duration ending on the supplied
        date. For example:
        ```py
        weeks(3).ending_on("2000-01-21")
        ```
        Returns:
        ```
        [
            (date(2000, 1, 1), date(2000, 1, 7)),
            (date(2000, 1, 8), date(2000, 1, 14)),
            (date(2000, 1, 15), date(2000, 1, 21)),
        ]
        ```

        Useful for generating the `intervals` arguments to [`Measures`](#Measures).
        """
        return self._generate_intervals(date, self.value, -1, "ending_on")

    @classmethod
    def _generate_intervals(cls, date, value, sign, method_name):
        date = parse_date_if_str(date)
        if not isinstance(date, datetime.date):
            raise TypeError(
                f"{cls.__name__}.{method_name}() can only be used with a literal "
                f"date, not a date series"
            )
        if not isinstance(value, int):
            raise TypeError(
                f"{cls.__name__}.{method_name}() can only be used with a literal "
                f"integer value, not an integer series"
            )
        if value < 0:
            raise ValueError(
                f"{cls.__name__}.{method_name}() can only be used with positive numbers"
            )
        return date_utils.generate_intervals(cls._date_add_static, date, value * sign)


class days(Duration):
    """
    Represents a duration of time specified in days
    """

    _date_add_static = staticmethod(date_utils.date_add_days)
    _date_add_qm = qm.Function.DateAddDays


class weeks(Duration):
    """
    Represents a duration of time specified in weeks
    """

    _date_add_static = staticmethod(date_utils.date_add_weeks)

    @staticmethod
    def _date_add_qm(date, num_weeks):
        num_days = qm.Function.Multiply(num_weeks, qm.Value(7))
        return qm.Function.DateAddDays(date, num_days)


class months(Duration):
    """
    Represents a duration of time specified in calendar months
    """

    _date_add_static = staticmethod(date_utils.date_add_months)
    _date_add_qm = qm.Function.DateAddMonths


class years(Duration):
    """
    Represents a duration of time specified in calendar years
    """

    _date_add_static = staticmethod(date_utils.date_add_years)
    _date_add_qm = qm.Function.DateAddYears


# CODE SERIES
#


class CodeFunctions:
    def _cast(self, value):
        if isinstance(value, str):
            return self._type(value)
        else:
            return value

    def to_category(self, categorisation, default=None):
        """
        An alias for `map_values` which makes the intention clearer when working with
        codelists. See [`codelist_from_csv()`](#codelist_from_csv).
        """
        return self.map_values(categorisation, default=default)


class CodePatientSeries(CodeFunctions, PatientSeries):
    _type = BaseCode


class CodeEventSeries(CodeFunctions, EventSeries):
    _type = BaseCode


# CONVERT QUERY MODEL SERIES TO EHRQL SERIES
#


def _wrap(qm_node):
    """
    Wrap a query model series in the ehrQL series class appropriate for its type and
    dimension
    """
    type_ = get_series_type(qm_node)
    is_patient_level = has_one_row_per_patient(qm_node)
    try:
        cls = REGISTERED_TYPES[type_, is_patient_level]
        return cls(qm_node)
    except KeyError:
        # If we don't have a match for exactly this type then we should have one for a
        # superclass
        matches = [
            cls
            for ((target_type, target_dimension), cls) in REGISTERED_TYPES.items()
            if issubclass(type_, target_type) and is_patient_level == target_dimension
        ]
        assert len(matches) == 1
        cls = matches[0]
        wrapped = cls(qm_node)
        wrapped._type = type_
        return wrapped


def _apply(qm_cls, *args):
    """
    Applies a query model operation `qm_cls` to its arguments which can be either ehrQL
    series or static values, returns an ehrQL series
    """
    # Convert all arguments into query model nodes
    qm_args = map(_convert, args)
    qm_node = qm_cls(*qm_args)
    # Wrap the resulting node back up in an ehrQL series
    return _wrap(qm_node)


def _convert(arg):
    # Unpack tuple arguments
    if isinstance(arg, tuple):
        return tuple(_convert(a) for a in arg)
    # Unpack dictionary arguments
    if isinstance(arg, _DictArg):
        return {_convert(key): _convert(value) for key, value in arg}
    # If it's an ehrQL series then get the wrapped query model node
    elif isinstance(arg, BaseSeries):
        return arg._qm_node
    # Otherwise it's a static value and needs to be put in a query model Value wrapper
    else:
        return qm.Value(arg)


def Parameter(name, type_):
    """
    Return a parameter or placeholder series which can be used to construct a query
    "template": a structure which can be turned into a query by substituing in concrete
    values for any parameters it contains
    """
    return _wrap(qm.Parameter(name, type_))


# FRAME TYPES
#


class BaseFrame:
    def __init__(self, qm_node):
        self._qm_node = qm_node

    def _select_column(self, name):
        return _wrap(qm.SelectColumn(source=self._qm_node, name=name))

    def exists_for_patient(self):
        """
        Return a [boolean patient series](#BoolPatientSeries) which is True for each
        patient that has a row in this frame and False otherwise.
        """
        return _wrap(qm.AggregateByPatient.Exists(source=self._qm_node))

    def count_for_patient(self):
        """
        Return an [integer patient series](#IntPatientSeries) giving the number of rows each
        patient has in this frame.

        Note this will be 0 rather than NULL if the patient has no rows at all in the frame.
        """
        return _wrap(qm.AggregateByPatient.Count(source=self._qm_node))


class PatientFrame(BaseFrame):
    """
    Frame containing at most one row per patient.
    """


class EventFrame(BaseFrame):
    """
    Frame which may contain multiple rows per patient.
    """

    def where(self, condition):
        """
        Return a new frame containing only the rows in this frame for which `condition`
        evaluates True.

        Note that this excludes any rows for which `condition` is NULL.
        """
        return self.__class__(
            qm.Filter(
                source=self._qm_node,
                condition=_convert(condition),
            )
        )

    def except_where(self, condition):
        """
        Return a new frame containing only the rows in this frame for which `condition`
        evaluates False or NULL i.e. the exact inverse of the rows included by
        `where()`.
        """
        return self.__class__(
            qm.Filter(
                source=self._qm_node,
                condition=qm.Function.Or(
                    lhs=qm.Function.Not(_convert(condition)),
                    rhs=qm.Function.IsNull(_convert(condition)),
                ),
            )
        )

    def sort_by(self, *sort_values):
        """
        Sort the rows for each patient by each of the supplied `sort_values`.

        Where more than one sort value is supplied then the first (i.e. left-most) value
        has highest priority and each subsequent sort value will only be used as a
        tie-breaker in case of an exact match among previous values.

        Note that NULL is considered smaller than any other value, so you may wish to
        filter out NULL values before sorting.
        """
        qm_node = self._qm_node
        # We expect series to be supplied highest priority first and, as the most
        # recently applied Sort operation has the highest priority, we need to apply
        # them in reverse order
        for series in reversed(sort_values):
            qm_node = qm.Sort(
                source=qm_node,
                sort_by=_convert(series),
            )
        cls = make_sorted_event_frame_class(self.__class__)
        return cls(qm_node)


class SortedEventFrameMethods:
    def first_for_patient(self):
        """
        Return a PatientFrame containing, for each patient, the first matching row
        according to whatever sort order has been applied.

        Note that where there are multiple rows tied for first place then the specific
        row returned is picked arbitrarily but consistently i.e. you shouldn't depend on
        getting any particular result, but the result you do get shouldn't change unless
        the data changes.
        """
        cls = make_patient_frame_class(self.__class__)
        return cls(
            qm.PickOneRowPerPatient(
                position=qm.Position.FIRST,
                source=self._qm_node,
            )
        )

    def last_for_patient(self):
        """
        Return a PatientFrame containing, for each patient, the last matching row
        according to whatever sort order has been applied.

        Note that where there are multiple rows tied for last place then the specific
        row returned is picked arbitrarily but consistently i.e. you shouldn't depend on
        getting any particular result, but the result you do get shouldn't change unless
        the data changes.
        """
        cls = make_patient_frame_class(self.__class__)
        return cls(
            qm.PickOneRowPerPatient(
                position=qm.Position.LAST,
                source=self._qm_node,
            )
        )


@functools.cache
def make_sorted_event_frame_class(cls):
    """
    Given a class return a subclass which has the SortedEventFrameMethods
    """
    if issubclass(cls, SortedEventFrameMethods):
        return cls
    else:
        return type(cls.__name__, (SortedEventFrameMethods, cls), {})


@functools.cache
def make_patient_frame_class(cls):
    """
    Given an EventFrame subclass return a PatientFrame subclass with the same columns as
    the original frame
    """
    return type(cls.__name__, (PatientFrame,), get_all_series_from_class(cls))


def get_all_series_from_class(cls):
    # Because `Series` is a descriptor we can't access the column objects via class
    # attributes without invoking the descriptor: instead, we have to access them using
    # `vars()`. But `vars()` only gives us attributes defined directly on the class, not
    # inherited ones. So we reproduce the inheritance behaviour using `ChainMap`.
    #
    # This is _almost_ exactly what `inspect.getmembers_static` does except that returns
    # attributes in lexical order whereas we want to return the original definition
    # order.
    attrs = ChainMap(*[vars(base) for base in cls.__mro__])
    return {key: value for key, value in attrs.items() if isinstance(value, Series)}


# FRAME CONSTRUCTOR ENTRYPOINTS
#


class SchemaError(Exception):
    ...


# A class decorator which replaces the class definition with an appropriately configured
# instance of the class. Obviously this is a _bit_ odd, but I think worth it overall.
# Using classes to define tables is (as far as I can tell) the only way to get nice
# autocomplete and type-checking behaviour for column names. But we don't actually want
# these classes accessible anywhere: users should only be interacting with instances of
# the classes, and having the classes themselves in the module namespaces only makes
# autocomplete more confusing and error prone.
def table(cls):
    try:
        qm_class = {
            (PatientFrame,): qm.SelectPatientTable,
            (EventFrame,): qm.SelectTable,
        }[cls.__bases__]
    except KeyError:
        raise SchemaError(
            "Schema class must subclass either `PatientFrame` or `EventFrame`"
        )

    qm_node = qm_class(
        name=cls.__name__,
        schema=get_table_schema_from_class(cls),
    )
    return cls(qm_node)


def get_table_schema_from_class(cls):
    # Get all `Series` objects on the class and determine the schema from them
    schema = {
        series.name: qm.Column(series.type_, constraints=series.constraints)
        for series in get_all_series_from_class(cls).values()
    }
    return qm.TableSchema(**schema)


# Defines a PatientFrame along with the data it contains. Takes a list (or
# any iterable) of row tuples of the form:
#
#    (patient_id, column_1_in_schema, column_2_in_schema, ...)
#
def table_from_rows(rows):
    def decorator(cls):
        if cls.__bases__ != (PatientFrame,):
            raise SchemaError("`@table_from_rows` can only be used with `PatientFrame`")
        qm_node = qm.InlinePatientTable(
            rows=tuple(rows),
            schema=get_table_schema_from_class(cls),
        )
        return cls(qm_node)

    return decorator


# Defines a PatientFrame along with the data it contains. Takes a path to
# a file (feather, csv, csv.gz) with rows of the form:
#
#    (patient_id, column_1_in_schema, column_2_in_schema, ...)
#
def table_from_file(path):
    path = Path(path)

    def decorator(cls):
        if cls.__bases__ != (PatientFrame,):
            raise SchemaError("`@table_from_file` can only be used with `PatientFrame`")

        schema = get_table_schema_from_class(cls)
        column_specs = get_column_specs_from_schema(schema)

        rows = read_dataset(path, column_specs)

        qm_node = qm.InlinePatientTable(
            rows=rows,
            schema=get_table_schema_from_class(cls),
        )
        return cls(qm_node)

    return decorator


# A descriptor which will return the appropriate type of series depending on the type of
# frame it belongs to i.e. a PatientSeries subclass for PatientFrames and an EventSeries
# subclass for EventFrames. This lets schema authors use a consistent syntax when
# defining frames of either type.
class Series:
    def __init__(
        self,
        type_,
        description="",
        constraints=(),
        required=True,
        implementation_notes_to_add_to_description="",
        notes_for_implementors="",
    ):
        self.type_ = type_
        self.description = strip_indent(description)
        self.constraints = constraints
        self.required = required
        self.implementation_notes_to_add_to_description = strip_indent(
            implementation_notes_to_add_to_description
        )
        self.notes_for_implementors = strip_indent(notes_for_implementors)

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:  # pragma: no cover
            return self
        return instance._select_column(self.name)


def get_tables_from_namespace(namespace):
    """
    Yield all ehrQL tables contained in `namespace`
    """
    for attr, value in vars(namespace).items():
        if isinstance(value, BaseFrame):
            yield attr, value


# CASE EXPRESSION FUNCTIONS
#


# TODO: There's no explicit error handling on using this wrong e.g. not calling `then()`
# or passing the wrong sort of thing as `condition`. The query model will prevent any
# invalid queries being created, but we should invest time in making the errors as
# immediate and as friendly as possible.
class when:
    def __init__(self, condition):
        self._condition = condition

    def then(self, value):
        return WhenThen(self._condition, value)


class WhenThen:
    def __init__(self, condition, value):
        self._condition = condition
        self._value = value

    def otherwise(self, default):
        return case(self, default=default)


def case(*when_thens, default=None):
    """
    Take a sequence of condition-values of the form:
    ```py
    when(condition).then(value)
    ```

    And evaluate them in order, returning the value of the first condition which
    evaluates True. If no condition matches and a `default` is specified then return
    that, otherwise return NULL.

    For example:
    ```py
    category = case(
        when(size < 10).then("small"),
        when(size < 20).then("medium"),
        when(size >= 20).then("large"),
        default="unknown",
    )
    ```

    Note that because the conditions are evaluated in order we don't need the condition
    for "medium" to specify `(size >= 10) & (size < 20)` because by the time the
    condition for "medium" is being evaluated we already know the condition for "small"
    is False.

    A simpler form is available when there is a single condition.  This example:
    ```py
    category = case(
        when(size < 15).then("small"),
        default="large",
    )
    ```

    can be rewritten as:
    ```py
    category = when(size < 15).then("small").otherwise("large")
    ```

    """
    cases = _DictArg((case._condition, case._value) for case in when_thens)
    # If we don't want a default then we shouldn't supply an argument, or else it will
    # get converted into `Value(None)` which is not what we want
    if default is None:
        return _apply(qm.Case, cases)
    else:
        return _apply(qm.Case, cases, default)


# HORIZONTAL AGGREGATION FUNCTIONS
#
def maximum_of(value, other_value, *other_values):
    """
    Return the maximum value of a collection of Series or Values, disregarding NULLs

    For example:
    ```py
    latest_event_date = maximum_of(event_series_1.date, event_series_2.date, "2001-01-01")
    ```
    """
    args = cast_all_arguments((value, other_value, *other_values))
    return _apply(qm.Function.MaximumOf, args)


def minimum_of(value, other_value, *other_values):
    """
    Return the minimum value of a collection of Series or Values, disregarding NULLs

    For example:
    ```py
    ealiest_event_date = minimum_of(event_series_1.date, event_series_2.date, "2001-01-01")
    ```
    """
    args = cast_all_arguments((value, other_value, *other_values))
    return _apply(qm.Function.MinimumOf, args)

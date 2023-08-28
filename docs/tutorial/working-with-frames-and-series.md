The explanations that follow make use of the [ehrQL sandbox](running-ehrql.md#sandbox-mode).

You can follow along by starting the sandbox:

```
opensafely exec ehrql:v0 sandbox example-data
```

and importing the tables that we want to interact with:

```pycon
>>> from ehrql.tables.beta.core import patients, medications
```

:notepad_spiral: The outputs below are truncated.

## Core types of object

### Series

A series represents a column of data,
and there are two types: patient series and event series.
A series either represents a column in a backend table,
or some columnar data that has been derived by transforming one or more columns in one or more backend tables.

#### Patient series

A patient series represents a column of data where there is no more than one value per patient.

For instance, a patient series containing dates of birth might look like:

```pycon
>>> patients.date_of_birth
0 | 1973-07-01
1 | 1948-03-01
2 | 2003-04-01
3 | 2007-06-01
...
```

In this output, the left-hand column shows the patient ID.

#### Event series

An event series represents a column of data where there can be multiple values per patient.

For instance, an event series containing medications dates might look like:

```pycon
>>> medications.date
0 | 0 | 2014-01-11
1 | 1 | 2015-08-06
1 | 2 | 2018-09-21
1 | 3 | 2020-05-17
3 | 4 | 2022-11-09
...
```

In this output, the left-hand column shows the patient ID
and the middle column shows the row number.

### Frames

A frame represents a table of data,
and contains one or more series.
A frame either represents a backend table,
or some tabular data that has been derived by transforming data from one or more backend tables.

#### Patient frames

A patient frame represents a table of data where there is no more than one row per patient.

For instance, a patient frame containing demographic data might look like:

```pycon
>>> patients
patient_id        | date_of_birth     | sex               | date_of_death
------------------+-------------------+-------------------+------------------
0                 | 1973-07-01        | female            | 2015-09-14
1                 | 1948-03-01        | male              | None
2                 | 2003-04-01        | male              | None
3                 | 2007-06-01        | female            | None
...
```

#### Event frames

An event frame represents a table of data where there may be multiple rows per patient.

For instance, an event frame containing medication data might look like:

```pycon
>>> medications
patient_id        | row_id            | date              | dmd_code
------------------+-------------------+-------------------+------------------
0                 | 0                 | 2014-01-11        | 39113611000001102
1                 | 1                 | 2015-08-06        | 39113611000001102
1                 | 2                 | 2018-09-21        | 39113311000001107
1                 | 3                 | 2020-05-17        | 22777311000001105
3                 | 4                 | 2022-11-09        | 22777311000001105
...
```

### Datasets

A dataset is a table containing **one row per patient**,
and **one column per feature of interest**.

The challenge is to **transform** the tables in an OpenSAFELY backend
(which are all either event frames or patient frames)
into one or more patient series that we can then add to a dataset definition.

## Transformations

### Transforming a frame into a series

Transforming an event frame or a patient frame into an event series or a patient series requires one step:
we select the column using Python’s attribute lookup notation.

We can transform the `patients` patient frame into a patient series like this:

```pycon
>>> patients.date_of_birth
0 | 1973-07-01
1 | 1948-03-01
2 | 2003-04-01
3 | 2007-06-01
...
```

### Transforming an event frame into a patient frame

Transforming an event frame into a patient frame involves selecting one row per patient.
We do this in two steps:

1. Choose one or more columns of the event frame to sort on.
2. Pick either the first or last row for each patient.

We can transform the `medications` event frame into a patient frame
containing just the earliest medication for each patient like this:

```pycon
>>> medications.sort_by(medications.date).first_for_patient()
patient_id        | date              | dmd_code
------------------+-------------------+------------------
0                 | 2014-01-11        | 39113611000001102
1                 | 2015-08-06        | 39113611000001102
3                 | 2022-11-09        | 22777311000001105
...
```

### Transforming an event frame into another event frame

An event frame can also be transformed into another event frame
by filtering for rows that do or do not match a given condition.

We can transform the `medications` event frame into another event frame
containing just the rows for 100mcg/dose Salbutamol like this:

```pycon
>>> medications.where(medications.dmd_code == "39113611000001102")
patient_id        | row_id            | date              | dmd_code
------------------+-------------------+-------------------+------------------
0                 | 0                 | 2014-01-11        | 39113611000001102
1                 | 1                 | 2015-08-06        | 39113611000001102
...
```

Alternatively we can transform the `medications` event frame into another event frame
containing all rows except the rows for 100mcg/dose Salbutamol like this:

```pycon
>>> medications.except_where(medications.dmd_code == "39113611000001102")
patient_id        | row_id            | date              | dmd_code
------------------+-------------------+-------------------+------------------
1                 | 2                 | 2018-09-21        | 39113311000001107
1                 | 3                 | 2020-05-17        | 22777311000001105
3                 | 4                 | 2022-11-09        | 22777311000001105
...
```

### Transforming one series into another

Finally, there are many ways a series can be transformed to produce another series.
We describe some of the most important and useful ways here.

#### Filtering an event frame for rows matching a condition

To filter an event frame for rows that match a given condition,
we need an event series with Boolean values.

We can do this by querying whether an event's code is in a list of codes:

```pycon
>>> medications.dmd_code.is_in(["39113311000001107", "39113611000001102"])
0 | 0 | True
1 | 1 | True
1 | 2 | True
1 | 3 | False
3 | 4 | False
...
```

Or we can do this by querying whether an event's date is before/after another date:

```pycon
>>> medications.date.is_on_or_after("2020-01-01")
0 | 0 | False
1 | 1 | False
1 | 2 | False
1 | 3 | True
3 | 4 | True
...
```

To see all of the available operations for filtering an event frame, see the reference docs [here](../reference/features.md#1-filtering-an-event-frame)

#### Extracting dates

Given a series of dates, we can extract the year (or month or day):

```pycon
>>> medications.date.year
0 | 0 | 2014
1 | 1 | 2015
1 | 2 | 2018
1 | 3 | 2020
3 | 4 | 2022
```

And we can perform arithmetic with dates:

```pycon
>>> from ehrql import days
>>> medications.date + days(30)
0 | 0 | 2014-02-10
1 | 1 | 2015-09-05
1 | 2 | 2018-10-21
1 | 3 | 2020-06-16
3 | 4 | 2022-12-09
...
```

To see all of the available operations for series containing dates, see the reference docs [here](../reference/features.md#11-operations-on-all-series-containing-dates)
"""
This schema defines the core tables and columns which should be available in any backend
providing primary care data, allowing dataset definitions written using this schema to
run across multiple backends.

!!! warning
    This schema is still a work-in-progress while the EMIS backend remains under
    development. Projects requiring EMIS data should continue to use the [Cohort
    Extractor](https://docs.opensafely.org/study-def/) tool.
"""
import datetime

from ehrql.codes import DMDCode, ICD10Code, SNOMEDCTCode
from ehrql.tables import Constraint, EventFrame, PatientFrame, Series, table


@table
class patients(PatientFrame):
    date_of_birth = Series(
        datetime.date,
        description="Patient's date of birth.",
        constraints=[Constraint.FirstOfMonth(), Constraint.NotNull()],
    )
    sex = Series(
        str,
        description="Patient's sex.",
        implementation_notes_to_add_to_description=(
            'Specify how this has been determined, e.g. "sex at birth", or "current sex".'
        ),
        constraints=[
            Constraint.Categorical(["female", "male", "intersex", "unknown"]),
            Constraint.NotNull(),
        ],
    )
    date_of_death = Series(
        datetime.date,
        description="Patient's date of death.",
    )

    def age_on(self, date):
        """
        Patient's age as an integer, in whole elapsed calendar years, as it would be on
        the given date.

        This method takes no account of whether the patient is alive on the given date.
        In particular, it may return negative values if the given date is before the
        patient's date of birth.
        """
        return (date - self.date_of_birth).years


@table
class ons_deaths(EventFrame):
    date = Series(
        datetime.date,
        description=(
            "Patient's date of death. "
            "Only deaths registered from February 2019 are recorded."
        ),
    )
    place = Series(
        str,
        constraints=[
            Constraint.Categorical(
                [
                    "Care Home",
                    "Elsewhere",
                    "Home",
                    "Hospice",
                    "Hospital",
                    "Other communal establishment",
                ]
            ),
        ],
    )
    underlying_cause_of_death = Series(ICD10Code)
    # TODO: Revisit this when we have support for multi-valued fields
    cause_of_death_01 = Series(ICD10Code)
    cause_of_death_02 = Series(ICD10Code)
    cause_of_death_03 = Series(ICD10Code)
    cause_of_death_04 = Series(ICD10Code)
    cause_of_death_05 = Series(ICD10Code)
    cause_of_death_06 = Series(ICD10Code)
    cause_of_death_07 = Series(ICD10Code)
    cause_of_death_08 = Series(ICD10Code)
    cause_of_death_09 = Series(ICD10Code)
    cause_of_death_10 = Series(ICD10Code)
    cause_of_death_11 = Series(ICD10Code)
    cause_of_death_12 = Series(ICD10Code)
    cause_of_death_13 = Series(ICD10Code)
    cause_of_death_14 = Series(ICD10Code)
    cause_of_death_15 = Series(ICD10Code)


@table
class clinical_events(EventFrame):
    date = Series(datetime.date)
    snomedct_code = Series(SNOMEDCTCode)
    numeric_value = Series(float)


@table
class medications(EventFrame):
    date = Series(datetime.date)
    dmd_code = Series(DMDCode)

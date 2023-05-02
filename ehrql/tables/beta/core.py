import datetime

from ehrql.codes import CTV3Code, DMDCode, ICD10Code, SNOMEDCTCode
from ehrql.tables import Constraint, EventFrame, PatientFrame, Series, table


@table
class patients(PatientFrame):
    date_of_birth = Series(
        datetime.date,
        description="Patient's date of birth, rounded to first of month",
        constraints=[Constraint.FirstOfMonth(), Constraint.NotNull()],
    )
    sex = Series(
        str,
        description="Patient's sex",
        implementation_notes_to_add_to_description=(
            'Specify how this has been determined, e.g. "sex at birth", or "current sex".'
        ),
        constraints=[
            Constraint.NotNull(),
            Constraint.Categorical(["female", "male", "intersex", "unknown"]),
        ],
    )
    date_of_death = Series(
        datetime.date,
        description="Patient's date of death",
    )

    def age_on(self, date):
        """
        Patient's age as an integer, in whole elapsed calendar years, as it would be on
        the supplied date.

        Note that this takes no account of whether the patient is alive at the given
        date. In particular, it may return negative values if the date is before the
        patient's date of birth.
        """
        return (date - self.date_of_birth).years


@table
class ons_deaths(EventFrame):
    date = Series(datetime.date)
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
    ctv3_code = Series(CTV3Code)
    numeric_value = Series(float)


@table
class medications(EventFrame):
    date = Series(datetime.date)
    dmd_code = Series(DMDCode)
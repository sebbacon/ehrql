# <strong>beta.tpp</strong> schema

Available on backends: [**TPP**](../../backends#tpp)

This schema defines the data (both primary care and externally linked) available in the
OpenSAFELY-TPP backend. For more information about this backend, see
"[SystmOne Primary Care](https://docs.opensafely.org/data-sources/systmone/)".

``` {.python .copy title='To use this schema in an ehrQL file:'}
from ehrql.tables.beta.tpp import (
    addresses,
    apcs,
    apcs_cost,
    appointments,
    clinical_events,
    ec,
    ec_cost,
    emergency_care_attendances,
    ethnicity_from_sus,
    hospital_admissions,
    household_memberships_2020,
    medications,
    occupation_on_covid_vaccine_record,
    ons_deaths,
    opa,
    opa_cost,
    opa_diag,
    opa_proc,
    open_prompt,
    patients,
    practice_registrations,
    sgss_covid_all_tests,
    vaccinations,
    wl_clockstops,
    wl_openpathways,
)
```

<p class="dimension-indicator"><code>many rows per patient</code></p>
## addresses

Geographic characteristics of the home address a patient registers with a practice.
Each row in this table is one registration period per patient.
Occasionally, a patient has multiple active registrations on a given date.
The postcode from the address is mapped to an Output Area,
from which other larger geographic representations can be derived
(see various [ONS publications][addresses_ukgeographies] for more detail).

!!! tip
    To group rounded IMD ranks by quintile:

    ```py
    imd = addresses.for_patient_on("2023-01-01").imd_rounded
    dataset.imd_quintile = case(
        when((imd >=0) & (imd < int(32844 * 1 / 5))).then("1 (most deprived)"),
        when(imd < int(32844 * 2 / 5)).then("2"),
        when(imd < int(32844 * 3 / 5)).then("3"),
        when(imd < int(32844 * 4 / 5)).then("4"),
        when(imd < int(32844 * 5 / 5)).then("5 (least deprived)"),
        default="unknown"
    )
    ```

[addresses_ukgeographies]: https://www.ons.gov.uk/methodology/geography/ukgeographies
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="addresses.address_id">
    <strong>address_id</strong>
    <a class="headerlink" href="#addresses.address_id" title="Permanent link">🔗</a>
    <code>integer</code>
  </dt>
  <dd markdown="block">
Unique address identifier.

  </dd>
</div>

<div markdown="block">
  <dt id="addresses.start_date">
    <strong>start_date</strong>
    <a class="headerlink" href="#addresses.start_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
Date patient moved to address.

  </dd>
</div>

<div markdown="block">
  <dt id="addresses.end_date">
    <strong>end_date</strong>
    <a class="headerlink" href="#addresses.end_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
Date patient moved out of address.

  </dd>
</div>

<div markdown="block">
  <dt id="addresses.address_type">
    <strong>address_type</strong>
    <a class="headerlink" href="#addresses.address_type" title="Permanent link">🔗</a>
    <code>integer</code>
  </dt>
  <dd markdown="block">
Type of address.

  </dd>
</div>

<div markdown="block">
  <dt id="addresses.rural_urban_classification">
    <strong>rural_urban_classification</strong>
    <a class="headerlink" href="#addresses.rural_urban_classification" title="Permanent link">🔗</a>
    <code>integer</code>
  </dt>
  <dd markdown="block">
Rural urban classification:

* 1 - Urban major conurbation
* 2 - Urban minor conurbation
* 3 - Urban city and town
* 4 - Urban city and town in a sparse setting
* 5 - Rural town and fringe
* 6 - Rural town and fringe in a sparse setting
* 7 - Rural village and dispersed
* 8 - Rural village and dispersed in a sparse setting

 * Always >= 1 and <= 8
  </dd>
</div>

<div markdown="block">
  <dt id="addresses.imd_rounded">
    <strong>imd_rounded</strong>
    <a class="headerlink" href="#addresses.imd_rounded" title="Permanent link">🔗</a>
    <code>integer</code>
  </dt>
  <dd markdown="block">
[Index of Multiple Deprivation][addresses_imd] (IMD)
rounded to the nearest 100, where lower values represent more deprived areas.

[addresses_imd]: https://www.gov.uk/government/statistics/english-indices-of-deprivation-2019

 * Always >= 0, <= 32800, and a multiple of 100
  </dd>
</div>

<div markdown="block">
  <dt id="addresses.msoa_code">
    <strong>msoa_code</strong>
    <a class="headerlink" href="#addresses.msoa_code" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
Middle Layer Super Output Areas (MSOA) code.

 * Matches regular expression: `E020[0-9]{5}`
  </dd>
</div>

<div markdown="block">
  <dt id="addresses.has_postcode">
    <strong>has_postcode</strong>
    <a class="headerlink" href="#addresses.has_postcode" title="Permanent link">🔗</a>
    <code>boolean</code>
  </dt>
  <dd markdown="block">
Indicating whether a valid postcode is recorded for the patient.

  </dd>
</div>

<div markdown="block">
  <dt id="addresses.care_home_is_potential_match">
    <strong>care_home_is_potential_match</strong>
    <a class="headerlink" href="#addresses.care_home_is_potential_match" title="Permanent link">🔗</a>
    <code>boolean</code>
  </dt>
  <dd markdown="block">
Indicating whether the patient's address matched with a care home, using TPP's algorithm.

  </dd>
</div>

<div markdown="block">
  <dt id="addresses.care_home_requires_nursing">
    <strong>care_home_requires_nursing</strong>
    <a class="headerlink" href="#addresses.care_home_requires_nursing" title="Permanent link">🔗</a>
    <code>boolean</code>
  </dt>
  <dd markdown="block">
Indicating whether the patient's address matched with a care home that required nursing.

  </dd>
</div>

<div markdown="block">
  <dt id="addresses.care_home_does_not_require_nursing">
    <strong>care_home_does_not_require_nursing</strong>
    <a class="headerlink" href="#addresses.care_home_does_not_require_nursing" title="Permanent link">🔗</a>
    <code>boolean</code>
  </dt>
  <dd markdown="block">
Indicating whether the patient's address matched with a care home that did not require nursing.

  </dd>
</div>

  </dl>
</div>
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Methods</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="addresses.for_patient_on">
    <strong>for_patient_on(</strong>date<strong>)</strong>
    <a class="headerlink" href="#addresses.for_patient_on" title="Permanent link">🔗</a>
    <code></code>
  </dt>
  <dd markdown="block">
Return each patient's registered address as it was on the supplied date.

Where there are multiple registered addresses we prefer any which have a known
postcode (though we never have access to this postcode) as this is used by TPP
to cross-reference other data associated with the address, such as the MSOA or
index of multiple deprevation.

Where there are multiple of these we prefer the most recently registered address
and then, if there are multiple of these, the one with the longest duration. If
there's stil an exact tie we choose arbitrarily based on the address ID.
    <details markdown="block">
    <summary>View method definition</summary>
```py
spanning_addrs = addresses.where(addresses.start_date <= date).except_where(
    addresses.end_date < date
)
ordered_addrs = spanning_addrs.sort_by(
    case(when(addresses.has_postcode).then(1), default=0),
    addresses.start_date,
    addresses.end_date,
    addresses.address_id,
)
return ordered_addrs.last_for_patient()

```
    </details>
  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## apcs

Admitted Patient Care Spells (APCS) data is provided via the NHS Secondary Uses Service.

This table gives core details of spells.

Each row is an in-hospital spell: a period of continuous care within a single trust.

Refer to the [OpenSAFELY documentation on the APCS data source][apcs_data_source_docs]
and the [GitHub issue discussing more of the background context][apcs_context_issue].

[apcs_data_source_docs]: https://docs.opensafely.org/data-sources/apc/
[apcs_context_issue]: https://github.com/opensafely-core/cohort-extractor/issues/186
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="apcs.apcs_ident">
    <strong>apcs_ident</strong>
    <a class="headerlink" href="#apcs.apcs_ident" title="Permanent link">🔗</a>
    <code>integer</code>
  </dt>
  <dd markdown="block">
Unique identifier for the spell used across the APCS tables.

 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="apcs.admission_date">
    <strong>admission_date</strong>
    <a class="headerlink" href="#apcs.admission_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
The admission date of the hospital provider spell.

  </dd>
</div>

<div markdown="block">
  <dt id="apcs.discharge_date">
    <strong>discharge_date</strong>
    <a class="headerlink" href="#apcs.discharge_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
The date of discharge from a hospital provider spell.

  </dd>
</div>

<div markdown="block">
  <dt id="apcs.spell_core_hrg_sus">
    <strong>spell_core_hrg_sus</strong>
    <a class="headerlink" href="#apcs.spell_core_hrg_sus" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
The core Healthcare Resource Group (HRG) code for the spell according to the derivations made by NHS Digital prior to import to the National Commissioning Data Repository (NCDR). HRGs are used to assign baseline tariff costs.

  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## apcs_cost

Admitted Patient Care Spells (APCS) data is provided via the NHS Secondary Uses Service.

This table gives details of spell cost.

Each row is an in-hospital spell: a period of continuous care within a single trust.

Note that data only goes back a couple of years.
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="apcs_cost.apcs_ident">
    <strong>apcs_ident</strong>
    <a class="headerlink" href="#apcs_cost.apcs_ident" title="Permanent link">🔗</a>
    <code>integer</code>
  </dt>
  <dd markdown="block">
Unique identifier for the spell used across the APCS tables.

 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="apcs_cost.grand_total_payment_mff">
    <strong>grand_total_payment_mff</strong>
    <a class="headerlink" href="#apcs_cost.grand_total_payment_mff" title="Permanent link">🔗</a>
    <code>float</code>
  </dt>
  <dd markdown="block">
The grand total payment for the activity (`Net_SLA_Payment + Tariff_MFF_Payment`) where SLA = service level agreement, i.e. all contractual payments which is national tariff for the type of activity **plus** any additional payments **minus** any applicable deductions. MFF = Market Forces Factor, a geography-based cost adjustment).

  </dd>
</div>

<div markdown="block">
  <dt id="apcs_cost.tariff_initial_amount">
    <strong>tariff_initial_amount</strong>
    <a class="headerlink" href="#apcs_cost.tariff_initial_amount" title="Permanent link">🔗</a>
    <code>float</code>
  </dt>
  <dd markdown="block">
The base national tariff.

  </dd>
</div>

<div markdown="block">
  <dt id="apcs_cost.tariff_total_payment">
    <strong>tariff_total_payment</strong>
    <a class="headerlink" href="#apcs_cost.tariff_total_payment" title="Permanent link">🔗</a>
    <code>float</code>
  </dt>
  <dd markdown="block">
The total payment according to the national tariff.

  </dd>
</div>

<div markdown="block">
  <dt id="apcs_cost.admission_date">
    <strong>admission_date</strong>
    <a class="headerlink" href="#apcs_cost.admission_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
The admission date of the hospital provider spell.

  </dd>
</div>

<div markdown="block">
  <dt id="apcs_cost.discharge_date">
    <strong>discharge_date</strong>
    <a class="headerlink" href="#apcs_cost.discharge_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
The date of discharge from a hospital provider spell.

  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## appointments

Appointments in primary care.

You can find out more about [the associated database table][appointments_5] in the [short data report][appointments_1].
It shows:

* Date ranges for `booked_date`, `start_date`, and `seen_date`
* Row counts by month for `booked_date` and `start_date`
* The distribution of lead times (`start_date - booked_date`)
* Row counts for each value of `status`

To view it, you will need a login for OpenSAFELY Jobs and the Project Collaborator
or Project Developer role for the [project][appointments_4]. The
[workspace][appointments_2] shows when the code that comprises the report was run;
the code itself is in the [appointments-short-data-report][appointments_3]
repository on GitHub.

!!! tip
    Querying this table is similar to using Cohort Extractor's
    `patients.with_gp_consultations` function. However, that function filters by
    the status of the appointment. To achieve a similar result with this table:

    ```py
    appointments.where(
        appointments.status.is_in([
            "Arrived",
            "In Progress",
            "Finished",
            "Visit",
            "Waiting",
            "Patient Walked Out",
        ])
    )
    ```

[appointments_1]: https://jobs.opensafely.org/curation-of-gp-appointments-data-short-data-report/appointments-short-data-report/outputs/latest/tpp/output/reports/report.html
[appointments_2]: https://jobs.opensafely.org/curation-of-gp-appointments-data-short-data-report/appointments-short-data-report/
[appointments_3]: https://github.com/opensafely/appointments-short-data-report
[appointments_4]: https://jobs.opensafely.org/curation-of-gp-appointments-data-short-data-report/
[appointments_5]: https://reports.opensafely.org/reports/opensafely-tpp-database-schema/#Appointment
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="appointments.booked_date">
    <strong>booked_date</strong>
    <a class="headerlink" href="#appointments.booked_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
The date the appointment was booked

  </dd>
</div>

<div markdown="block">
  <dt id="appointments.start_date">
    <strong>start_date</strong>
    <a class="headerlink" href="#appointments.start_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
The date the appointment was due to start

  </dd>
</div>

<div markdown="block">
  <dt id="appointments.seen_date">
    <strong>seen_date</strong>
    <a class="headerlink" href="#appointments.seen_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
The date the patient was seen

  </dd>
</div>

<div markdown="block">
  <dt id="appointments.status">
    <strong>status</strong>
    <a class="headerlink" href="#appointments.status" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
The status of the appointment

 * Possible values: `Booked`, `Arrived`, `Did Not Attend`, `In Progress`, `Finished`, `Requested`, `Blocked`, `Visit`, `Waiting`, `Cancelled by Patient`, `Cancelled by Unit`, `Cancelled by Other Service`, `No Access Visit`, `Cancelled Due To Death`, `Patient Walked Out`
  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## clinical_events

Each record corresponds to a single clinical or consultation event for a patient.

Each event is recorded twice: once with a CTv3 code, and again with the equivalent
SNOMED-CT code. Each record will have only one of the ctv3_code or snomedct_code
columns set and the other will be null. This allows you to query the table using
either a CTv3 codelist or SNOMED-CT codelist and all records using the other coding
system will be effectively ignored.

Note that event codes do not change in this table. If an event code in the coding
system becomes inactive, the event will still be coded to the inactive code.
As such, codelists should include all relevant inactive codes.

Detailed information on onward referrals is not currently available. A subset of
referrals are recorded in the clinical events table but this data will be incomplete.
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="clinical_events.date">
    <strong>date</strong>
    <a class="headerlink" href="#clinical_events.date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="clinical_events.snomedct_code">
    <strong>snomedct_code</strong>
    <a class="headerlink" href="#clinical_events.snomedct_code" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="clinical_events.ctv3_code">
    <strong>ctv3_code</strong>
    <a class="headerlink" href="#clinical_events.ctv3_code" title="Permanent link">🔗</a>
    <code>CTV3 (Read v3) code</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="clinical_events.numeric_value">
    <strong>numeric_value</strong>
    <a class="headerlink" href="#clinical_events.numeric_value" title="Permanent link">🔗</a>
    <code>float</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## ec

Emergency care attendances data — the Emergency Care Data Set (ECDS) —
is provided via the NHS Secondary Uses Service.

This table gives core details of attendances.

Refer to the [OpenSAFELY documentation on the ECDS data source][ecds_data_source_docs]
and the GitHub issue that [discusses more of the background context][ecds_context_issue].

[ecds_data_source_docs]: https://docs.opensafely.org/data-sources/ecds/
[ecds_context_issue]: https://github.com/opensafely-core/cohort-extractor/issues/182
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="ec.ec_ident">
    <strong>ec_ident</strong>
    <a class="headerlink" href="#ec.ec_ident" title="Permanent link">🔗</a>
    <code>integer</code>
  </dt>
  <dd markdown="block">
Unique identifier for the attendance used across the EC tables.

 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="ec.arrival_date">
    <strong>arrival_date</strong>
    <a class="headerlink" href="#ec.arrival_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
The date the patient self presented at the accident & emergency department, or arrived in an ambulance at the accident & emergency department.

  </dd>
</div>

<div markdown="block">
  <dt id="ec.sus_hrg_code">
    <strong>sus_hrg_code</strong>
    <a class="headerlink" href="#ec.sus_hrg_code" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
The core Healthcare Resource Group (HRG) code derived by sus+, used for tariff application.

  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## ec_cost

Emergency care attendances data is provided via the NHS Secondary Uses Service.

This table gives details of attendance costs.
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="ec_cost.ec_ident">
    <strong>ec_ident</strong>
    <a class="headerlink" href="#ec_cost.ec_ident" title="Permanent link">🔗</a>
    <code>integer</code>
  </dt>
  <dd markdown="block">
Unique identifier for the attendance used across the EC tables.

 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="ec_cost.grand_total_payment_mff">
    <strong>grand_total_payment_mff</strong>
    <a class="headerlink" href="#ec_cost.grand_total_payment_mff" title="Permanent link">🔗</a>
    <code>float</code>
  </dt>
  <dd markdown="block">
The grand total payment for the activity (`Net_SLA_Payment + Tariff_MFF_Payment`) where SLA = service level agreement, i.e. all contractual payments which is national tariff for the type of activity **plus** any additional payments **minus** any applicable deductions. MFF = Market Forces Factor, a geography-based cost adjustment).

  </dd>
</div>

<div markdown="block">
  <dt id="ec_cost.tariff_total_payment">
    <strong>tariff_total_payment</strong>
    <a class="headerlink" href="#ec_cost.tariff_total_payment" title="Permanent link">🔗</a>
    <code>float</code>
  </dt>
  <dd markdown="block">
The total payment according to the national tariff.

  </dd>
</div>

<div markdown="block">
  <dt id="ec_cost.arrival_date">
    <strong>arrival_date</strong>
    <a class="headerlink" href="#ec_cost.arrival_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
The date the patient self presented at the accident & emergency department, or arrived in an ambulance at the accident & emergency department.

  </dd>
</div>

<div markdown="block">
  <dt id="ec_cost.ec_decision_to_admit_date">
    <strong>ec_decision_to_admit_date</strong>
    <a class="headerlink" href="#ec_cost.ec_decision_to_admit_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
The date a decision to admit was made (if applicable).

  </dd>
</div>

<div markdown="block">
  <dt id="ec_cost.ec_injury_date">
    <strong>ec_injury_date</strong>
    <a class="headerlink" href="#ec_cost.ec_injury_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
The date the patient was injured (if applicable).

  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## emergency_care_attendances

Emergency care attendances data is provided via the NHS Secondary Uses Service.

This table gives details of attendances.

Note that there is a limited number of diagnoses allowed within this dataset,
and so will not match with the range of diagnoses allowed in other datasets
such as the primary care record.
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="emergency_care_attendances.id">
    <strong>id</strong>
    <a class="headerlink" href="#emergency_care_attendances.id" title="Permanent link">🔗</a>
    <code>integer</code>
  </dt>
  <dd markdown="block">
Unique identifier for the attendance used across the EC tables.

 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="emergency_care_attendances.arrival_date">
    <strong>arrival_date</strong>
    <a class="headerlink" href="#emergency_care_attendances.arrival_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
The date the patient self presented at the accident & emergency department, or arrived in an ambulance at the accident & emergency department.

  </dd>
</div>

<div markdown="block">
  <dt id="emergency_care_attendances.discharge_destination">
    <strong>discharge_destination</strong>
    <a class="headerlink" href="#emergency_care_attendances.discharge_destination" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
  </dt>
  <dd markdown="block">
The SNOMED CT concept ID which is used to identify the intended destination of the patient following discharge from the emergency care department.

  </dd>
</div>

<div markdown="block">
  <dt id="emergency_care_attendances.diagnosis_01">
    <strong>diagnosis_01</strong>
    <a class="headerlink" href="#emergency_care_attendances.diagnosis_01" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
  </dt>
  <dd markdown="block">
The SNOMED CT concept ID which is used to identify the patient diagnosis. Note that only a limited subset of SNOMED CT codes are used; see the [NHS Data Model and Dictionary entry for emergency care diagnosis](https://www.datadictionary.nhs.uk/data_elements/emergency_care_diagnosis__snomed_ct_.html).

  </dd>
</div>

<div markdown="block">
  <dt id="emergency_care_attendances.diagnosis_02">
    <strong>diagnosis_02</strong>
    <a class="headerlink" href="#emergency_care_attendances.diagnosis_02" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
  </dt>
  <dd markdown="block">
The SNOMED CT concept ID which is used to identify the patient diagnosis. Note that only a limited subset of SNOMED CT codes are used; see the [NHS Data Model and Dictionary entry for emergency care diagnosis](https://www.datadictionary.nhs.uk/data_elements/emergency_care_diagnosis__snomed_ct_.html).

  </dd>
</div>

<div markdown="block">
  <dt id="emergency_care_attendances.diagnosis_03">
    <strong>diagnosis_03</strong>
    <a class="headerlink" href="#emergency_care_attendances.diagnosis_03" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
  </dt>
  <dd markdown="block">
The SNOMED CT concept ID which is used to identify the patient diagnosis. Note that only a limited subset of SNOMED CT codes are used; see the [NHS Data Model and Dictionary entry for emergency care diagnosis](https://www.datadictionary.nhs.uk/data_elements/emergency_care_diagnosis__snomed_ct_.html).

  </dd>
</div>

<div markdown="block">
  <dt id="emergency_care_attendances.diagnosis_04">
    <strong>diagnosis_04</strong>
    <a class="headerlink" href="#emergency_care_attendances.diagnosis_04" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
  </dt>
  <dd markdown="block">
The SNOMED CT concept ID which is used to identify the patient diagnosis. Note that only a limited subset of SNOMED CT codes are used; see the [NHS Data Model and Dictionary entry for emergency care diagnosis](https://www.datadictionary.nhs.uk/data_elements/emergency_care_diagnosis__snomed_ct_.html).

  </dd>
</div>

<div markdown="block">
  <dt id="emergency_care_attendances.diagnosis_05">
    <strong>diagnosis_05</strong>
    <a class="headerlink" href="#emergency_care_attendances.diagnosis_05" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
  </dt>
  <dd markdown="block">
The SNOMED CT concept ID which is used to identify the patient diagnosis. Note that only a limited subset of SNOMED CT codes are used; see the [NHS Data Model and Dictionary entry for emergency care diagnosis](https://www.datadictionary.nhs.uk/data_elements/emergency_care_diagnosis__snomed_ct_.html).

  </dd>
</div>

<div markdown="block">
  <dt id="emergency_care_attendances.diagnosis_06">
    <strong>diagnosis_06</strong>
    <a class="headerlink" href="#emergency_care_attendances.diagnosis_06" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
  </dt>
  <dd markdown="block">
The SNOMED CT concept ID which is used to identify the patient diagnosis. Note that only a limited subset of SNOMED CT codes are used; see the [NHS Data Model and Dictionary entry for emergency care diagnosis](https://www.datadictionary.nhs.uk/data_elements/emergency_care_diagnosis__snomed_ct_.html).

  </dd>
</div>

<div markdown="block">
  <dt id="emergency_care_attendances.diagnosis_07">
    <strong>diagnosis_07</strong>
    <a class="headerlink" href="#emergency_care_attendances.diagnosis_07" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
  </dt>
  <dd markdown="block">
The SNOMED CT concept ID which is used to identify the patient diagnosis. Note that only a limited subset of SNOMED CT codes are used; see the [NHS Data Model and Dictionary entry for emergency care diagnosis](https://www.datadictionary.nhs.uk/data_elements/emergency_care_diagnosis__snomed_ct_.html).

  </dd>
</div>

<div markdown="block">
  <dt id="emergency_care_attendances.diagnosis_08">
    <strong>diagnosis_08</strong>
    <a class="headerlink" href="#emergency_care_attendances.diagnosis_08" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
  </dt>
  <dd markdown="block">
The SNOMED CT concept ID which is used to identify the patient diagnosis. Note that only a limited subset of SNOMED CT codes are used; see the [NHS Data Model and Dictionary entry for emergency care diagnosis](https://www.datadictionary.nhs.uk/data_elements/emergency_care_diagnosis__snomed_ct_.html).

  </dd>
</div>

<div markdown="block">
  <dt id="emergency_care_attendances.diagnosis_09">
    <strong>diagnosis_09</strong>
    <a class="headerlink" href="#emergency_care_attendances.diagnosis_09" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
  </dt>
  <dd markdown="block">
The SNOMED CT concept ID which is used to identify the patient diagnosis. Note that only a limited subset of SNOMED CT codes are used; see the [NHS Data Model and Dictionary entry for emergency care diagnosis](https://www.datadictionary.nhs.uk/data_elements/emergency_care_diagnosis__snomed_ct_.html).

  </dd>
</div>

<div markdown="block">
  <dt id="emergency_care_attendances.diagnosis_10">
    <strong>diagnosis_10</strong>
    <a class="headerlink" href="#emergency_care_attendances.diagnosis_10" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
  </dt>
  <dd markdown="block">
The SNOMED CT concept ID which is used to identify the patient diagnosis. Note that only a limited subset of SNOMED CT codes are used; see the [NHS Data Model and Dictionary entry for emergency care diagnosis](https://www.datadictionary.nhs.uk/data_elements/emergency_care_diagnosis__snomed_ct_.html).

  </dd>
</div>

<div markdown="block">
  <dt id="emergency_care_attendances.diagnosis_11">
    <strong>diagnosis_11</strong>
    <a class="headerlink" href="#emergency_care_attendances.diagnosis_11" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
  </dt>
  <dd markdown="block">
The SNOMED CT concept ID which is used to identify the patient diagnosis. Note that only a limited subset of SNOMED CT codes are used; see the [NHS Data Model and Dictionary entry for emergency care diagnosis](https://www.datadictionary.nhs.uk/data_elements/emergency_care_diagnosis__snomed_ct_.html).

  </dd>
</div>

<div markdown="block">
  <dt id="emergency_care_attendances.diagnosis_12">
    <strong>diagnosis_12</strong>
    <a class="headerlink" href="#emergency_care_attendances.diagnosis_12" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
  </dt>
  <dd markdown="block">
The SNOMED CT concept ID which is used to identify the patient diagnosis. Note that only a limited subset of SNOMED CT codes are used; see the [NHS Data Model and Dictionary entry for emergency care diagnosis](https://www.datadictionary.nhs.uk/data_elements/emergency_care_diagnosis__snomed_ct_.html).

  </dd>
</div>

<div markdown="block">
  <dt id="emergency_care_attendances.diagnosis_13">
    <strong>diagnosis_13</strong>
    <a class="headerlink" href="#emergency_care_attendances.diagnosis_13" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
  </dt>
  <dd markdown="block">
The SNOMED CT concept ID which is used to identify the patient diagnosis. Note that only a limited subset of SNOMED CT codes are used; see the [NHS Data Model and Dictionary entry for emergency care diagnosis](https://www.datadictionary.nhs.uk/data_elements/emergency_care_diagnosis__snomed_ct_.html).

  </dd>
</div>

<div markdown="block">
  <dt id="emergency_care_attendances.diagnosis_14">
    <strong>diagnosis_14</strong>
    <a class="headerlink" href="#emergency_care_attendances.diagnosis_14" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
  </dt>
  <dd markdown="block">
The SNOMED CT concept ID which is used to identify the patient diagnosis. Note that only a limited subset of SNOMED CT codes are used; see the [NHS Data Model and Dictionary entry for emergency care diagnosis](https://www.datadictionary.nhs.uk/data_elements/emergency_care_diagnosis__snomed_ct_.html).

  </dd>
</div>

<div markdown="block">
  <dt id="emergency_care_attendances.diagnosis_15">
    <strong>diagnosis_15</strong>
    <a class="headerlink" href="#emergency_care_attendances.diagnosis_15" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
  </dt>
  <dd markdown="block">
The SNOMED CT concept ID which is used to identify the patient diagnosis. Note that only a limited subset of SNOMED CT codes are used; see the [NHS Data Model and Dictionary entry for emergency care diagnosis](https://www.datadictionary.nhs.uk/data_elements/emergency_care_diagnosis__snomed_ct_.html).

  </dd>
</div>

<div markdown="block">
  <dt id="emergency_care_attendances.diagnosis_16">
    <strong>diagnosis_16</strong>
    <a class="headerlink" href="#emergency_care_attendances.diagnosis_16" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
  </dt>
  <dd markdown="block">
The SNOMED CT concept ID which is used to identify the patient diagnosis. Note that only a limited subset of SNOMED CT codes are used; see the [NHS Data Model and Dictionary entry for emergency care diagnosis](https://www.datadictionary.nhs.uk/data_elements/emergency_care_diagnosis__snomed_ct_.html).

  </dd>
</div>

<div markdown="block">
  <dt id="emergency_care_attendances.diagnosis_17">
    <strong>diagnosis_17</strong>
    <a class="headerlink" href="#emergency_care_attendances.diagnosis_17" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
  </dt>
  <dd markdown="block">
The SNOMED CT concept ID which is used to identify the patient diagnosis. Note that only a limited subset of SNOMED CT codes are used; see the [NHS Data Model and Dictionary entry for emergency care diagnosis](https://www.datadictionary.nhs.uk/data_elements/emergency_care_diagnosis__snomed_ct_.html).

  </dd>
</div>

<div markdown="block">
  <dt id="emergency_care_attendances.diagnosis_18">
    <strong>diagnosis_18</strong>
    <a class="headerlink" href="#emergency_care_attendances.diagnosis_18" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
  </dt>
  <dd markdown="block">
The SNOMED CT concept ID which is used to identify the patient diagnosis. Note that only a limited subset of SNOMED CT codes are used; see the [NHS Data Model and Dictionary entry for emergency care diagnosis](https://www.datadictionary.nhs.uk/data_elements/emergency_care_diagnosis__snomed_ct_.html).

  </dd>
</div>

<div markdown="block">
  <dt id="emergency_care_attendances.diagnosis_19">
    <strong>diagnosis_19</strong>
    <a class="headerlink" href="#emergency_care_attendances.diagnosis_19" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
  </dt>
  <dd markdown="block">
The SNOMED CT concept ID which is used to identify the patient diagnosis. Note that only a limited subset of SNOMED CT codes are used; see the [NHS Data Model and Dictionary entry for emergency care diagnosis](https://www.datadictionary.nhs.uk/data_elements/emergency_care_diagnosis__snomed_ct_.html).

  </dd>
</div>

<div markdown="block">
  <dt id="emergency_care_attendances.diagnosis_20">
    <strong>diagnosis_20</strong>
    <a class="headerlink" href="#emergency_care_attendances.diagnosis_20" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
  </dt>
  <dd markdown="block">
The SNOMED CT concept ID which is used to identify the patient diagnosis. Note that only a limited subset of SNOMED CT codes are used; see the [NHS Data Model and Dictionary entry for emergency care diagnosis](https://www.datadictionary.nhs.uk/data_elements/emergency_care_diagnosis__snomed_ct_.html).

  </dd>
</div>

<div markdown="block">
  <dt id="emergency_care_attendances.diagnosis_21">
    <strong>diagnosis_21</strong>
    <a class="headerlink" href="#emergency_care_attendances.diagnosis_21" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
  </dt>
  <dd markdown="block">
The SNOMED CT concept ID which is used to identify the patient diagnosis. Note that only a limited subset of SNOMED CT codes are used; see the [NHS Data Model and Dictionary entry for emergency care diagnosis](https://www.datadictionary.nhs.uk/data_elements/emergency_care_diagnosis__snomed_ct_.html).

  </dd>
</div>

<div markdown="block">
  <dt id="emergency_care_attendances.diagnosis_22">
    <strong>diagnosis_22</strong>
    <a class="headerlink" href="#emergency_care_attendances.diagnosis_22" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
  </dt>
  <dd markdown="block">
The SNOMED CT concept ID which is used to identify the patient diagnosis. Note that only a limited subset of SNOMED CT codes are used; see the [NHS Data Model and Dictionary entry for emergency care diagnosis](https://www.datadictionary.nhs.uk/data_elements/emergency_care_diagnosis__snomed_ct_.html).

  </dd>
</div>

<div markdown="block">
  <dt id="emergency_care_attendances.diagnosis_23">
    <strong>diagnosis_23</strong>
    <a class="headerlink" href="#emergency_care_attendances.diagnosis_23" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
  </dt>
  <dd markdown="block">
The SNOMED CT concept ID which is used to identify the patient diagnosis. Note that only a limited subset of SNOMED CT codes are used; see the [NHS Data Model and Dictionary entry for emergency care diagnosis](https://www.datadictionary.nhs.uk/data_elements/emergency_care_diagnosis__snomed_ct_.html).

  </dd>
</div>

<div markdown="block">
  <dt id="emergency_care_attendances.diagnosis_24">
    <strong>diagnosis_24</strong>
    <a class="headerlink" href="#emergency_care_attendances.diagnosis_24" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
  </dt>
  <dd markdown="block">
The SNOMED CT concept ID which is used to identify the patient diagnosis. Note that only a limited subset of SNOMED CT codes are used; see the [NHS Data Model and Dictionary entry for emergency care diagnosis](https://www.datadictionary.nhs.uk/data_elements/emergency_care_diagnosis__snomed_ct_.html).

  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>one row per patient</code></p>
## ethnicity_from_sus

This finds the most frequently used national ethnicity code for each patient from
the various SUS (Secondary Uses Service) tables.

Specifically it uses ethnicity codes from the following tables:

    APCS (In-patient hospital admissions)
    EC (A&E attendances)
    OPA (Out-patient hospital appointments)

Codes are as defined by "Ethnic Category Code 2001" — the 16+1 ethnic data
categories used in the 2001 census:
https://www.datadictionary.nhs.uk/data_elements/ethnic_category.html

Codes beginning Z ("Not stated") and 99 ("Not known") are excluded.

Where there is a tie for the most common code the lexically greatest code is used.
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="ethnicity_from_sus.code">
    <strong>code</strong>
    <a class="headerlink" href="#ethnicity_from_sus.code" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
First character of recorded ethncity code (national code):
https://www.datadictionary.nhs.uk/data_elements/ethnic_category.html

 * Possible values: `A`, `B`, `C`, `D`, `E`, `F`, `G`, `H`, `J`, `K`, `L`, `M`, `N`, `P`, `R`, `S`
  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## hospital_admissions


<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="hospital_admissions.id">
    <strong>id</strong>
    <a class="headerlink" href="#hospital_admissions.id" title="Permanent link">🔗</a>
    <code>integer</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="hospital_admissions.admission_date">
    <strong>admission_date</strong>
    <a class="headerlink" href="#hospital_admissions.admission_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="hospital_admissions.discharge_date">
    <strong>discharge_date</strong>
    <a class="headerlink" href="#hospital_admissions.discharge_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="hospital_admissions.admission_method">
    <strong>admission_method</strong>
    <a class="headerlink" href="#hospital_admissions.admission_method" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="hospital_admissions.all_diagnoses">
    <strong>all_diagnoses</strong>
    <a class="headerlink" href="#hospital_admissions.all_diagnoses" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="hospital_admissions.patient_classification">
    <strong>patient_classification</strong>
    <a class="headerlink" href="#hospital_admissions.patient_classification" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="hospital_admissions.days_in_critical_care">
    <strong>days_in_critical_care</strong>
    <a class="headerlink" href="#hospital_admissions.days_in_critical_care" title="Permanent link">🔗</a>
    <code>integer</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="hospital_admissions.primary_diagnoses">
    <strong>primary_diagnoses</strong>
    <a class="headerlink" href="#hospital_admissions.primary_diagnoses" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
Note that the underlying data only contains a single diagnosis code, despite the "diagnoses" name. primary_diagnoses is therefore deprecated and will be removed in future: use primary_diagnosis instead.

  </dd>
</div>

<div markdown="block">
  <dt id="hospital_admissions.primary_diagnosis">
    <strong>primary_diagnosis</strong>
    <a class="headerlink" href="#hospital_admissions.primary_diagnosis" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>one row per patient</code></p>
## household_memberships_2020

Inferred household membership as of 2020-02-01, as determined by TPP using an as yet
undocumented algorithm.
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="household_memberships_2020.household_pseudo_id">
    <strong>household_pseudo_id</strong>
    <a class="headerlink" href="#household_memberships_2020.household_pseudo_id" title="Permanent link">🔗</a>
    <code>integer</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="household_memberships_2020.household_size">
    <strong>household_size</strong>
    <a class="headerlink" href="#household_memberships_2020.household_size" title="Permanent link">🔗</a>
    <code>integer</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## medications


<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="medications.date">
    <strong>date</strong>
    <a class="headerlink" href="#medications.date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="medications.dmd_code">
    <strong>dmd_code</strong>
    <a class="headerlink" href="#medications.dmd_code" title="Permanent link">🔗</a>
    <code>dm+d code</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## occupation_on_covid_vaccine_record


<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="occupation_on_covid_vaccine_record.is_healthcare_worker">
    <strong>is_healthcare_worker</strong>
    <a class="headerlink" href="#occupation_on_covid_vaccine_record.is_healthcare_worker" title="Permanent link">🔗</a>
    <code>boolean</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>one row per patient</code></p>
## ons_deaths

Registered deaths

Date and cause of death based on information recorded when deaths are
certified and registered in England and Wales from February 2019 onwards.
The data provider is the Office for National Statistics (ONS).
This table is updated approximately weekly in OpenSAFELY.

This table includes the underlying cause of death and up to 15 medical conditions mentioned on the death certificate.
These codes (`cause_of_death_01` to `cause_of_death_15`) are not ordered meaningfully.

More information about this table can be found in following documents provided by the ONS:

- [Information collected at death registration](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/deaths/methodologies/userguidetomortalitystatisticsjuly2017#information-collected-at-death-registration)
- [User guide to mortality statistics](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/deaths/methodologies/userguidetomortalitystatisticsjuly2017)
- [How death registrations are recorded and stored by ONS](https://www.ons.gov.uk/aboutus/transparencyandgovernance/freedomofinformationfoi/howdeathregistrationsarerecordedandstoredbyons)

In the associated database table [ONS_Deaths](https://reports.opensafely.org/reports/opensafely-tpp-database-schema/#ONS_Deaths),
a small number of patients have multiple registered deaths.
This table contains the earliest registered death.
The `ehrql.tables.beta.raw.ons_deaths` table contains all registered deaths.
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="ons_deaths.date">
    <strong>date</strong>
    <a class="headerlink" href="#ons_deaths.date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
Patient's date of death.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.place">
    <strong>place</strong>
    <a class="headerlink" href="#ons_deaths.place" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
Patient's date of death.

 * Possible values: `Care Home`, `Elsewhere`, `Home`, `Hospice`, `Hospital`, `Other communal establishment`
  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.underlying_cause_of_death">
    <strong>underlying_cause_of_death</strong>
    <a class="headerlink" href="#ons_deaths.underlying_cause_of_death" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Patient's underlying cause of death of death.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_01">
    <strong>cause_of_death_01</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_01" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_02">
    <strong>cause_of_death_02</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_02" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_03">
    <strong>cause_of_death_03</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_03" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_04">
    <strong>cause_of_death_04</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_04" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_05">
    <strong>cause_of_death_05</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_05" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_06">
    <strong>cause_of_death_06</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_06" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_07">
    <strong>cause_of_death_07</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_07" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_08">
    <strong>cause_of_death_08</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_08" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_09">
    <strong>cause_of_death_09</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_09" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_10">
    <strong>cause_of_death_10</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_10" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_11">
    <strong>cause_of_death_11</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_11" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_12">
    <strong>cause_of_death_12</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_12" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_13">
    <strong>cause_of_death_13</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_13" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_14">
    <strong>cause_of_death_14</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_14" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_15">
    <strong>cause_of_death_15</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_15" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## opa

Outpatient appointments data (OPA) is provided via the NHS Secondary Uses Service.

This table gives core details of outpatient appointments.

Refer to the GitHub issue that [describes limitations
of the outpatient appointments data][opa_limitations_issue]
and the GitHub issue that [discusses more of the background context][opa_context_issue].

[opa_limitations_issue]: https://github.com/opensafely-core/cohort-extractor/issues/673
[opa_context_issue]: https://github.com/opensafely-core/cohort-extractor/issues/492
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="opa.opa_ident">
    <strong>opa_ident</strong>
    <a class="headerlink" href="#opa.opa_ident" title="Permanent link">🔗</a>
    <code>integer</code>
  </dt>
  <dd markdown="block">
Unique identifier for the appointment used across the OPA tables.

 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="opa.appointment_date">
    <strong>appointment_date</strong>
    <a class="headerlink" href="#opa.appointment_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
The date of an appointment.

  </dd>
</div>

<div markdown="block">
  <dt id="opa.attendance_status">
    <strong>attendance_status</strong>
    <a class="headerlink" href="#opa.attendance_status" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
Indicates whether or not an appointment for a care contact took place. If the appointment did not take place it also indicates whether or not advanced warning was given. Refer to the [NHS Data Model and Dictionary entry for "attended or did not attend"](https://www.datadictionary.nhs.uk/data_elements/attended_or_did_not_attend_code.html) for details on code meanings.

 * Possible values: `5`, `6`, `7`, `2`, `3`, `4`, `0`
  </dd>
</div>

<div markdown="block">
  <dt id="opa.consultation_medium_used">
    <strong>consultation_medium_used</strong>
    <a class="headerlink" href="#opa.consultation_medium_used" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
Identifies the communication mechanism used to relay information between the care professional and the person who is the subject of the consultation, during a care activity. Refer to the [NHS Data Model and Dictionary entry for "consultation mechanism"](https://www.datadictionary.nhs.uk/data_elements/consultation_mechanism.html) for details on code meanings. Note that the allowed codes as listed in TPP's data appear to be a subset of the codes listed in the NHS Data Model and Dictionary.

 * Possible values: `01`, `02`, `03`, `04`, `05`, `09`, `10`, `11`, `98`
  </dd>
</div>

<div markdown="block">
  <dt id="opa.first_attendance">
    <strong>first_attendance</strong>
    <a class="headerlink" href="#opa.first_attendance" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
An indication of whether a patient is making a first attendance or contact; or a follow-up attendance or contact and whether the consultation medium used national code was face to face communication or telephone or telemedicine web camera. Refer to the [NHS Data Model and Dictionary entry for "first attendance"](https://www.datadictionary.nhs.uk/attributes/first_attendance.html) for details on code meanings. Note that the allowed codes as listed in TPP's data contain an additional `9` code over the NHS Data Model and Dictionary entry.

 * Possible values: `1`, `2`, `3`, `4`, `5`, `9`
  </dd>
</div>

<div markdown="block">
  <dt id="opa.hrg_code">
    <strong>hrg_code</strong>
    <a class="headerlink" href="#opa.hrg_code" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
The Healthcare Resource Group (HRG) code assigned to the activity, used to assign baseline tariff costs.

  </dd>
</div>

<div markdown="block">
  <dt id="opa.treatment_function_code">
    <strong>treatment_function_code</strong>
    <a class="headerlink" href="#opa.treatment_function_code" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
The treatment function under which the patient is treated. It may be the same as the main specialty code or a different treatment function which will be the care professional's treatment interest.

  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## opa_cost

Outpatient appointments data is provided via the NHS Secondary Uses Service.

This table gives details of outpatient appointment costs.

Note that data only goes back a couple of years.
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="opa_cost.opa_ident">
    <strong>opa_ident</strong>
    <a class="headerlink" href="#opa_cost.opa_ident" title="Permanent link">🔗</a>
    <code>integer</code>
  </dt>
  <dd markdown="block">
Unique identifier for the appointment used across the OPA tables.

 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="opa_cost.tariff_opp">
    <strong>tariff_opp</strong>
    <a class="headerlink" href="#opa_cost.tariff_opp" title="Permanent link">🔗</a>
    <code>float</code>
  </dt>
  <dd markdown="block">
The base national tariff where the procedure tariff is applicable.

  </dd>
</div>

<div markdown="block">
  <dt id="opa_cost.grand_total_payment_mff">
    <strong>grand_total_payment_mff</strong>
    <a class="headerlink" href="#opa_cost.grand_total_payment_mff" title="Permanent link">🔗</a>
    <code>float</code>
  </dt>
  <dd markdown="block">
The grand total payment for the activity (`Net_SLA_Payment + Tariff_MFF_Payment`) where SLA = service level agreement, i.e. all contractual payments which is national tariff for the type of activity **plus** any additional payments **minus** any applicable deductions. MFF = Market Forces Factor, a geography-based cost adjustment).

  </dd>
</div>

<div markdown="block">
  <dt id="opa_cost.tariff_total_payment">
    <strong>tariff_total_payment</strong>
    <a class="headerlink" href="#opa_cost.tariff_total_payment" title="Permanent link">🔗</a>
    <code>float</code>
  </dt>
  <dd markdown="block">
The total payment according to the national tariff.

  </dd>
</div>

<div markdown="block">
  <dt id="opa_cost.appointment_date">
    <strong>appointment_date</strong>
    <a class="headerlink" href="#opa_cost.appointment_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
The date of an appointment.

  </dd>
</div>

<div markdown="block">
  <dt id="opa_cost.referral_request_received_date">
    <strong>referral_request_received_date</strong>
    <a class="headerlink" href="#opa_cost.referral_request_received_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
The date the referral request was received by the health care provider.

  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## opa_diag

Outpatient appointments data is provided via the NHS Secondary Uses Service.

This table gives details of outpatient appointment diagnoses.

Note that diagnoses are often absent from outpatient records.
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="opa_diag.opa_ident">
    <strong>opa_ident</strong>
    <a class="headerlink" href="#opa_diag.opa_ident" title="Permanent link">🔗</a>
    <code>integer</code>
  </dt>
  <dd markdown="block">
Unique identifier for the appointment used across the OPA tables.

 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="opa_diag.primary_diagnosis_code">
    <strong>primary_diagnosis_code</strong>
    <a class="headerlink" href="#opa_diag.primary_diagnosis_code" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
The international classification of diseases (ICD) code used to identify the primary patient diagnosis. Note that this will typically not be completed.

  </dd>
</div>

<div markdown="block">
  <dt id="opa_diag.primary_diagnosis_code_read">
    <strong>primary_diagnosis_code_read</strong>
    <a class="headerlink" href="#opa_diag.primary_diagnosis_code_read" title="Permanent link">🔗</a>
    <code>CTV3 (Read v3) code</code>
  </dt>
  <dd markdown="block">
The Read coded clinical terms code to identify the primary patient diagnosis. Note that this will typically not be completed.

  </dd>
</div>

<div markdown="block">
  <dt id="opa_diag.secondary_diagnosis_code_1">
    <strong>secondary_diagnosis_code_1</strong>
    <a class="headerlink" href="#opa_diag.secondary_diagnosis_code_1" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
The international classification of diseases (ICD) code used to identify the secondary patient diagnosis. Note that this will typically not be completed.

  </dd>
</div>

<div markdown="block">
  <dt id="opa_diag.secondary_diagnosis_code_1_read">
    <strong>secondary_diagnosis_code_1_read</strong>
    <a class="headerlink" href="#opa_diag.secondary_diagnosis_code_1_read" title="Permanent link">🔗</a>
    <code>CTV3 (Read v3) code</code>
  </dt>
  <dd markdown="block">
The Read coded clinical terms used to identify the secondary patient diagnosis. Note that this will typically not be completed.

  </dd>
</div>

<div markdown="block">
  <dt id="opa_diag.appointment_date">
    <strong>appointment_date</strong>
    <a class="headerlink" href="#opa_diag.appointment_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
The date of an appointment.

  </dd>
</div>

<div markdown="block">
  <dt id="opa_diag.referral_request_received_date">
    <strong>referral_request_received_date</strong>
    <a class="headerlink" href="#opa_diag.referral_request_received_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
The date the referral request was received by the health care provider.

  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## opa_proc

Outpatient appointments data is provided via the NHS Secondary Uses Service.

This table gives details of outpatient procedures.
Typically, procedures will only be recorded where they attract a specified payment.
The majority of appointments will have no procedure recorded.
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="opa_proc.opa_ident">
    <strong>opa_ident</strong>
    <a class="headerlink" href="#opa_proc.opa_ident" title="Permanent link">🔗</a>
    <code>integer</code>
  </dt>
  <dd markdown="block">
Unique identifier for the appointment used across the OPA tables.

 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="opa_proc.primary_procedure_code">
    <strong>primary_procedure_code</strong>
    <a class="headerlink" href="#opa_proc.primary_procedure_code" title="Permanent link">🔗</a>
    <code>OPCS-4 code</code>
  </dt>
  <dd markdown="block">
The OPCS classification of interventions and procedures code which is used to identify the primary patient procedure carried out.

  </dd>
</div>

<div markdown="block">
  <dt id="opa_proc.primary_procedure_code_read">
    <strong>primary_procedure_code_read</strong>
    <a class="headerlink" href="#opa_proc.primary_procedure_code_read" title="Permanent link">🔗</a>
    <code>CTV3 (Read v3) code</code>
  </dt>
  <dd markdown="block">
The Read coded clinical terms code which is used to identify the primary patient procedure carried out.

  </dd>
</div>

<div markdown="block">
  <dt id="opa_proc.procedure_code_1">
    <strong>procedure_code_1</strong>
    <a class="headerlink" href="#opa_proc.procedure_code_1" title="Permanent link">🔗</a>
    <code>OPCS-4 code</code>
  </dt>
  <dd markdown="block">
TODO

  </dd>
</div>

<div markdown="block">
  <dt id="opa_proc.procedure_code_2_read">
    <strong>procedure_code_2_read</strong>
    <a class="headerlink" href="#opa_proc.procedure_code_2_read" title="Permanent link">🔗</a>
    <code>CTV3 (Read v3) code</code>
  </dt>
  <dd markdown="block">
The Read coded clinical terms for a procedure other than the primary procedure.

  </dd>
</div>

<div markdown="block">
  <dt id="opa_proc.appointment_date">
    <strong>appointment_date</strong>
    <a class="headerlink" href="#opa_proc.appointment_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
The date of an appointment.

  </dd>
</div>

<div markdown="block">
  <dt id="opa_proc.referral_request_received_date">
    <strong>referral_request_received_date</strong>
    <a class="headerlink" href="#opa_proc.referral_request_received_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
The date the referral request was received by the health care provider.

  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## open_prompt

This table contains responses to questions from the OpenPROMPT project.

You can find out more about this table in the associated short data report. To view
it, you will need a login for [Level 4][open_prompt_1]. The
[workspace][open_prompt_2] shows when the code that comprises the report was run;
the code itself is in the [airmid-short-data-report][open_prompt_3] repository on
GitHub.

[open_prompt_1]: https://docs.opensafely.org/security-levels/#level-4-nhs-england-are-data-controllers-of-the-data
[open_prompt_2]: https://jobs.opensafely.org/datalab/opensafely-internal/airmid-short-data-report/
[open_prompt_3]: https://github.com/opensafely/airmid-short-data-report
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="open_prompt.ctv3_code">
    <strong>ctv3_code</strong>
    <a class="headerlink" href="#open_prompt.ctv3_code" title="Permanent link">🔗</a>
    <code>CTV3 (Read v3) code</code>
  </dt>
  <dd markdown="block">
The response to the question, as a CTV3 code. Alternatively, if the question does not admit a CTV3 code as the response, then the question, as a CTV3 code.

 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="open_prompt.snomedct_code">
    <strong>snomedct_code</strong>
    <a class="headerlink" href="#open_prompt.snomedct_code" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
  </dt>
  <dd markdown="block">
The response to the question, as a SNOMED CT code. Alternatively, if the question does not admit a SNOMED CT code as the response, then the question, as a SNOMED CT code.

  </dd>
</div>

<div markdown="block">
  <dt id="open_prompt.creation_date">
    <strong>creation_date</strong>
    <a class="headerlink" href="#open_prompt.creation_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
The date the survey was administered

 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="open_prompt.consultation_date">
    <strong>consultation_date</strong>
    <a class="headerlink" href="#open_prompt.consultation_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
The response to the question, as a date, if the question admits a date as the response. Alternatively, the date the survey was administered.

 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="open_prompt.consultation_id">
    <strong>consultation_id</strong>
    <a class="headerlink" href="#open_prompt.consultation_id" title="Permanent link">🔗</a>
    <code>integer</code>
  </dt>
  <dd markdown="block">
The ID of the survey

 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="open_prompt.numeric_value">
    <strong>numeric_value</strong>
    <a class="headerlink" href="#open_prompt.numeric_value" title="Permanent link">🔗</a>
    <code>float</code>
  </dt>
  <dd markdown="block">
The response to the question, as a number

  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>one row per patient</code></p>
## patients

Patients in primary care.

### Representativeness

You can find out more about the representativeness of these data in the
OpenSAFELY-TPP backend in:

> The OpenSAFELY Collaborative, Colm D. Andrews, Anna Schultze, Helen J. Curtis, William J. Hulme, John Tazare, Stephen J. W. Evans, _et al._ 2022.
> "OpenSAFELY: Representativeness of Electronic Health Record Platform OpenSAFELY-TPP Data Compared to the Population of England."
> Wellcome Open Res 2022, 7:191.
> <https://doi.org/10.12688/wellcomeopenres.18010.1>


### Orphan records

If a practice becomes aware that a patient has moved house,
then the practice _deducts_, or removes, the patient's records from their register.
If the patient doesn't register with a new practice within a given amount of time
(normally from four to eight weeks),
then the patient's records are permanently deducted and are _orphan records_.
There are roughly 1.6 million orphan records.
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="patients.date_of_birth">
    <strong>date_of_birth</strong>
    <a class="headerlink" href="#patients.date_of_birth" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
Patient's date of birth.

 * Always the first day of a month
 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="patients.sex">
    <strong>sex</strong>
    <a class="headerlink" href="#patients.sex" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
Patient's sex.

 * Possible values: `female`, `male`, `intersex`, `unknown`
 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="patients.date_of_death">
    <strong>date_of_death</strong>
    <a class="headerlink" href="#patients.date_of_death" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
Patient's date of death.

  </dd>
</div>

  </dl>
</div>
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Methods</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="patients.age_on">
    <strong>age_on(</strong>date<strong>)</strong>
    <a class="headerlink" href="#patients.age_on" title="Permanent link">🔗</a>
    <code></code>
  </dt>
  <dd markdown="block">
Patient's age as an integer, in whole elapsed calendar years, as it would be on
the given date.

This method takes no account of whether the patient is alive on the given date.
In particular, it may return negative values if the given date is before the
patient's date of birth.
    <details markdown="block">
    <summary>View method definition</summary>
```py
return (date - patients.date_of_birth).years

```
    </details>
  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## practice_registrations

Each record corresponds to a patient's registration with a practice.

Only patients with a full GMS (General Medical Services) registration are included.

We have registration history for:

* all patients currently registered at a TPP practice
* all patients registered at a TPP practice any time from 1 Jan 2009 onwards:
    * who have since de-registered
    * who have since died

A patient can be registered with zero, one, or more than one practices at a given
time. For instance, students are often registered with a practice at home and a
practice at university.
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="practice_registrations.start_date">
    <strong>start_date</strong>
    <a class="headerlink" href="#practice_registrations.start_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
Date patient joined practice.

 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="practice_registrations.end_date">
    <strong>end_date</strong>
    <a class="headerlink" href="#practice_registrations.end_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
Date patient left practice.

  </dd>
</div>

<div markdown="block">
  <dt id="practice_registrations.practice_pseudo_id">
    <strong>practice_pseudo_id</strong>
    <a class="headerlink" href="#practice_registrations.practice_pseudo_id" title="Permanent link">🔗</a>
    <code>integer</code>
  </dt>
  <dd markdown="block">
Pseudonymised practice identifier.

 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="practice_registrations.practice_stp">
    <strong>practice_stp</strong>
    <a class="headerlink" href="#practice_registrations.practice_stp" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
ONS code of practice's STP (Sustainability and Transformation Partnership).
STPs have been replaced by ICBs (Integrated Care Boards), and ICB codes will be available soon.

 * Matches regular expression: `E540000[0-9]{2}`
  </dd>
</div>

<div markdown="block">
  <dt id="practice_registrations.practice_nuts1_region_name">
    <strong>practice_nuts1_region_name</strong>
    <a class="headerlink" href="#practice_registrations.practice_nuts1_region_name" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
Name of the NUTS level 1 region of England to which the practice belongs.
For more information see:
<https://www.ons.gov.uk/methodology/geography/ukgeographies/eurostat>

 * Possible values: `North East`, `North West`, `Yorkshire and The Humber`, `East Midlands`, `West Midlands`, `East`, `London`, `South East`, `South West`
  </dd>
</div>

  </dl>
</div>
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Methods</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="practice_registrations.for_patient_on">
    <strong>for_patient_on(</strong>date<strong>)</strong>
    <a class="headerlink" href="#practice_registrations.for_patient_on" title="Permanent link">🔗</a>
    <code></code>
  </dt>
  <dd markdown="block">
Return each patient's practice registration as it was on the supplied date.

Where a patient is registered with multiple practices we prefer the most recent
registration and then, if there are multiple of these, the one with the longest
duration. If there's stil an exact tie we choose arbitrarily based on the
practice ID.
    <details markdown="block">
    <summary>View method definition</summary>
```py
spanning_regs = practice_registrations.where(practice_registrations.start_date <= date).except_where(
    practice_registrations.end_date < date
)
ordered_regs = spanning_regs.sort_by(
    practice_registrations.start_date,
    practice_registrations.end_date,
    practice_registrations.practice_pseudo_id,
)
return ordered_regs.last_for_patient()

```
    </details>
  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## sgss_covid_all_tests

COVID-19 tests results from SGSS (the Second Generation Surveillance System).

For background on this data see the NHS [DARS catalogue entry][DARS_SGSS].
And for more detail on SGSS in general see [PHE_Laboratory_Reporting_Guidelines.pdf][PHE_LRG].

[PHE_LRG]: https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/739854/PHE_Laboratory_Reporting_Guidelines.pdf
[DARS_SGSS]: https://digital.nhs.uk/services/data-access-request-service-dars/dars-products-and-services/data-set-catalogue/covid-19-second-generation-surveillance-system-sgss
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="sgss_covid_all_tests.specimen_taken_date">
    <strong>specimen_taken_date</strong>
    <a class="headerlink" href="#sgss_covid_all_tests.specimen_taken_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
Date on which specimen was collected.

 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="sgss_covid_all_tests.is_positive">
    <strong>is_positive</strong>
    <a class="headerlink" href="#sgss_covid_all_tests.is_positive" title="Permanent link">🔗</a>
    <code>boolean</code>
  </dt>
  <dd markdown="block">
Whether the specimin tested positive for SARS-CoV-2.

 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="sgss_covid_all_tests.lab_report_date">
    <strong>lab_report_date</strong>
    <a class="headerlink" href="#sgss_covid_all_tests.lab_report_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
Date on which the labaratory reported the result.

 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="sgss_covid_all_tests.was_symptomatic">
    <strong>was_symptomatic</strong>
    <a class="headerlink" href="#sgss_covid_all_tests.was_symptomatic" title="Permanent link">🔗</a>
    <code>boolean</code>
  </dt>
  <dd markdown="block">
Whether the patient reported symptoms of COVID-19 at the time the specimen
was collected. May be NULL if unknown.

  </dd>
</div>

<div markdown="block">
  <dt id="sgss_covid_all_tests.sgtf_status">
    <strong>sgtf_status</strong>
    <a class="headerlink" href="#sgss_covid_all_tests.sgtf_status" title="Permanent link">🔗</a>
    <code>integer</code>
  </dt>
  <dd markdown="block">
Provides information on whether a PCR test result exhibited "S-Gene Target
Failure" which can be used as a proxy for the presence of certain Variants
of Concern.

Results are provided as number between 0 and 9. We know the meaning of
_some_ of these numbers based on an email from PHE:

> 0: S gene detected<br>
> Detectable S gene (CH3>0)<br>
> Detectable y ORF1ab CT value (CH1) <=30 and >0<br>
> Detectable N gene CT value (CH2) <=30 and >0<br>
>
> 1: Isolate with confirmed SGTF<br>
> Undetectable S gene; CT value (CH3) =0<br>
> Detectable ORF1ab gene; CT value (CH2) <=30 and >0<br>
> Detectable N gene; CT value (CH1) <=30 and >0<br>
>
> 9: Cannot be classified
>
> Null are where the target is not S Gene. I think LFTs are currently
> also coming across as 9 so will need to review those to null as well as
> clearly this is a PCR only variable.

However the values 2, 4 and 8 also occur in this column and we don't
currently have documentation on their meaning.

 * Always >= 0 and <= 9
  </dd>
</div>

<div markdown="block">
  <dt id="sgss_covid_all_tests.variant">
    <strong>variant</strong>
    <a class="headerlink" href="#sgss_covid_all_tests.variant" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
Where a specific SARS-CoV-2 variant was identified this column provides the details.

This appears to be effectively a free-text field with a large variety of
possible values. Some have an obvious meaning e.g. `B.1.617.2`,
`VOC-21JAN-02`, `VUI-21FEB-04`.

Others less so e.g. `VOC-22JAN-O1_probable:V-21OCT-01_low-qc`.

  </dd>
</div>

<div markdown="block">
  <dt id="sgss_covid_all_tests.variant_detection_method">
    <strong>variant_detection_method</strong>
    <a class="headerlink" href="#sgss_covid_all_tests.variant_detection_method" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
Where a specific SARS-CoV-2 variant was identified this provides the method
used to do so.

 * Possible values: `Private Lab Sequencing`, `Reflex Assay`, `Sanger Provisional Result`
  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## vaccinations

This table contains information on administered vaccinations,
identified using either the target disease (e.g., Influenza),
or the vaccine product name (e.g., Optaflu).
For more information about this table see the
"[Vaccinaton names in the OpenSAFELY-TPP database][vaccinations_1]" report.

Vaccinations that were administered at work or in a pharmacy might not be
included in this table.

[vaccinations_1]: https://reports.opensafely.org/reports/opensafely-tpp-vaccination-names/
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="vaccinations.vaccination_id">
    <strong>vaccination_id</strong>
    <a class="headerlink" href="#vaccinations.vaccination_id" title="Permanent link">🔗</a>
    <code>integer</code>
  </dt>
  <dd markdown="block">
Vaccination identifier.

  </dd>
</div>

<div markdown="block">
  <dt id="vaccinations.date">
    <strong>date</strong>
    <a class="headerlink" href="#vaccinations.date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
The date the vaccination was administered.

  </dd>
</div>

<div markdown="block">
  <dt id="vaccinations.target_disease">
    <strong>target_disease</strong>
    <a class="headerlink" href="#vaccinations.target_disease" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
Vaccine's target disease.

  </dd>
</div>

<div markdown="block">
  <dt id="vaccinations.product_name">
    <strong>product_name</strong>
    <a class="headerlink" href="#vaccinations.product_name" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
Vaccine's product name.

  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## wl_clockstops

National Waiting List Clock Stops

This dataset contains all completed referral-to-treatment (RTT) pathways with a "clock stop" date between May 2021 and May 2022.
Patients referred for non-emergency consultant-led treatment are on RTT pathways.
The "clock start" date is the date of the first referral that starts the pathway.
The "clock stop" date is when the patient either: receives treatment;
declines treatment;
enters a period of active monitoring;
no longer requires treatment;
or dies.
The time spent waiting is the difference in these two dates.

A patient may have multiple rows if they have multiple completed RTT pathways;
however, there is only one row per unique pathway.
Because referral identifiers aren't necessarily unique between hospitals,
unique RTT pathways can be identified using a combination of:

* `pseudo_organisation_code_patient_pathway_identifier_issuer`
* `pseudo_patient_pathway_identifier`
* `pseudo_referral_identifier`
* `referral_to_treatment_period_start_date`

For more information, see
"[Consultant-led Referral to Treatment Waiting Times Rules and Guidance][wl_clockstops_1]".

[wl_clockstops_1]: https://www.england.nhs.uk/statistics/statistical-work-areas/rtt-waiting-times/rtt-guidance/
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="wl_clockstops.activity_treatment_function_code">
    <strong>activity_treatment_function_code</strong>
    <a class="headerlink" href="#wl_clockstops.activity_treatment_function_code" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
The treatment function

 * Matches regular expression: `[a-zA-Z0-9]{3}`
  </dd>
</div>

<div markdown="block">
  <dt id="wl_clockstops.priority_type_code">
    <strong>priority_type_code</strong>
    <a class="headerlink" href="#wl_clockstops.priority_type_code" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
The priority type

 * Possible values: `routine`, `urgent`, `two week wait`
  </dd>
</div>

<div markdown="block">
  <dt id="wl_clockstops.pseudo_organisation_code_patient_pathway_identifier_issuer">
    <strong>pseudo_organisation_code_patient_pathway_identifier_issuer</strong>
    <a class="headerlink" href="#wl_clockstops.pseudo_organisation_code_patient_pathway_identifier_issuer" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="wl_clockstops.pseudo_patient_pathway_identifier">
    <strong>pseudo_patient_pathway_identifier</strong>
    <a class="headerlink" href="#wl_clockstops.pseudo_patient_pathway_identifier" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="wl_clockstops.pseudo_referral_identifier">
    <strong>pseudo_referral_identifier</strong>
    <a class="headerlink" href="#wl_clockstops.pseudo_referral_identifier" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="wl_clockstops.referral_request_received_date">
    <strong>referral_request_received_date</strong>
    <a class="headerlink" href="#wl_clockstops.referral_request_received_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
The date the referral was received, for the referral that started the original pathway

  </dd>
</div>

<div markdown="block">
  <dt id="wl_clockstops.referral_to_treatment_period_end_date">
    <strong>referral_to_treatment_period_end_date</strong>
    <a class="headerlink" href="#wl_clockstops.referral_to_treatment_period_end_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
Clock stop for the completed pathway

  </dd>
</div>

<div markdown="block">
  <dt id="wl_clockstops.referral_to_treatment_period_start_date">
    <strong>referral_to_treatment_period_start_date</strong>
    <a class="headerlink" href="#wl_clockstops.referral_to_treatment_period_start_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
Clock start for the completed pathway

  </dd>
</div>

<div markdown="block">
  <dt id="wl_clockstops.source_of_referral_for_outpatients">
    <strong>source_of_referral_for_outpatients</strong>
    <a class="headerlink" href="#wl_clockstops.source_of_referral_for_outpatients" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="wl_clockstops.waiting_list_type">
    <strong>waiting_list_type</strong>
    <a class="headerlink" href="#wl_clockstops.waiting_list_type" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
The waiting list type on completion of the pathway

 * Possible values: `ORTT`, `IRTT`
  </dd>
</div>

<div markdown="block">
  <dt id="wl_clockstops.week_ending_date">
    <strong>week_ending_date</strong>
    <a class="headerlink" href="#wl_clockstops.week_ending_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
The Sunday of the week that the pathway relates to

  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## wl_openpathways

National Waiting List Open Pathways

This dataset contains all people on open (incomplete) RTT or not current RTT (non-RTT) pathways as of May 2022.
It is a snapshot of everyone still awaiting treatment as of May 2022 (i.e., the clock hasn't stopped).
Patients referred for non-emergency consultant-led treatment are on RTT pathways,
while patients referred for non-consultant-led treatment are on non-RTT pathways.
For each pathway, there is one row for every week that the patient is still waiting.
Because referral identifiers aren't necessarily unique between hospitals,
unique RTT pathways can be identified using a combination of:

* `pseudo_organisation_code_patient_pathway_identifier_issuer`
* `pseudo_patient_pathway_identifier`
* `pseudo_referral_identifier`
* `referral_to_treatment_period_start_date`


For more information, see
"[Consultant-led Referral to Treatment Waiting Times Rules and Guidance][wl_openpathways_1]".

[wl_openpathways_1]: https://www.england.nhs.uk/statistics/statistical-work-areas/rtt-waiting-times/rtt-guidance/
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="wl_openpathways.activity_treatment_function_code">
    <strong>activity_treatment_function_code</strong>
    <a class="headerlink" href="#wl_openpathways.activity_treatment_function_code" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
The treatment function

 * Matches regular expression: `[a-zA-Z0-9]{3}`
  </dd>
</div>

<div markdown="block">
  <dt id="wl_openpathways.current_pathway_period_start_date">
    <strong>current_pathway_period_start_date</strong>
    <a class="headerlink" href="#wl_openpathways.current_pathway_period_start_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
Latest clock start for this pathway period

  </dd>
</div>

<div markdown="block">
  <dt id="wl_openpathways.priority_type_code">
    <strong>priority_type_code</strong>
    <a class="headerlink" href="#wl_openpathways.priority_type_code" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
The priority type

 * Possible values: `routine`, `urgent`, `two week wait`
  </dd>
</div>

<div markdown="block">
  <dt id="wl_openpathways.pseudo_organisation_code_patient_pathway_identifier_issuer">
    <strong>pseudo_organisation_code_patient_pathway_identifier_issuer</strong>
    <a class="headerlink" href="#wl_openpathways.pseudo_organisation_code_patient_pathway_identifier_issuer" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="wl_openpathways.pseudo_patient_pathway_identifier">
    <strong>pseudo_patient_pathway_identifier</strong>
    <a class="headerlink" href="#wl_openpathways.pseudo_patient_pathway_identifier" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="wl_openpathways.pseudo_referral_identifier">
    <strong>pseudo_referral_identifier</strong>
    <a class="headerlink" href="#wl_openpathways.pseudo_referral_identifier" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="wl_openpathways.referral_request_received_date">
    <strong>referral_request_received_date</strong>
    <a class="headerlink" href="#wl_openpathways.referral_request_received_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
The date the referral was received, for the referral that started the original pathway

  </dd>
</div>

<div markdown="block">
  <dt id="wl_openpathways.referral_to_treatment_period_end_date">
    <strong>referral_to_treatment_period_end_date</strong>
    <a class="headerlink" href="#wl_openpathways.referral_to_treatment_period_end_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
If the pathway is open, then `NULL`

  </dd>
</div>

<div markdown="block">
  <dt id="wl_openpathways.referral_to_treatment_period_start_date">
    <strong>referral_to_treatment_period_start_date</strong>
    <a class="headerlink" href="#wl_openpathways.referral_to_treatment_period_start_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
Latest clock start for this pathway. If the pathway is not a current pathway, then `NULL`.

  </dd>
</div>

<div markdown="block">
  <dt id="wl_openpathways.source_of_referral">
    <strong>source_of_referral</strong>
    <a class="headerlink" href="#wl_openpathways.source_of_referral" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
National referral source code for the referral that created the original pathway

 * Matches regular expression: `[a-zA-Z0-9]{2}`
  </dd>
</div>

<div markdown="block">
  <dt id="wl_openpathways.waiting_list_type">
    <strong>waiting_list_type</strong>
    <a class="headerlink" href="#wl_openpathways.waiting_list_type" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">


 * Possible values: `ORTT`, `IRTT`, `ONON`, `INON`
  </dd>
</div>

<div markdown="block">
  <dt id="wl_openpathways.week_ending_date">
    <strong>week_ending_date</strong>
    <a class="headerlink" href="#wl_openpathways.week_ending_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
The Sunday of the week that the pathway relates to

  </dd>
</div>

  </dl>
</div>

import functools
import random
import string
import time
from datetime import date, timedelta

import structlog

from ehrql.dummy_data.query_info import QueryInfo
from ehrql.query_engines.in_memory import InMemoryQueryEngine
from ehrql.query_engines.in_memory_database import InMemoryDatabase
from ehrql.tables import Constraint
from ehrql.utils.orm_utils import orm_classes_from_tables
from ehrql.utils.regex_utils import create_regex_generator


log = structlog.getLogger()


CHARS = string.ascii_letters + string.digits + ".-+_"

# Use caching to avoid constantly re-creating the generators
get_regex_generator = functools.cache(create_regex_generator)


class DummyDataGenerator:
    def __init__(
        self,
        variable_definitions,
        population_size=500,
        batch_size=5000,
        random_seed="BwRV3spP",
        timeout=60,
    ):
        self.variable_definitions = variable_definitions
        self.population_size = population_size
        self.batch_size = batch_size
        self.random_seed = random_seed
        self.timeout = timeout
        self.patient_generator = DummyPatientGenerator(
            self.variable_definitions, self.random_seed
        )

    def get_data(self):
        generator = self.patient_generator
        data = []
        found = 0

        # Create a version of the query with just the population definition, and an
        # in-memory engine to run it against
        population_query = {"population": self.variable_definitions["population"]}
        database = InMemoryDatabase()
        engine = InMemoryQueryEngine(database)

        log.info(
            f"Attempting to generate {self.population_size} matching patients "
            f"(random seed: {self.random_seed}, timeout: {self.timeout}s)"
        )
        start = time.time()

        for batch_start in range(1, 2**63, self.batch_size):
            # Generate batches of patient data (just enough to determine population
            # membership) and find those matching the population definition
            patient_batch = {
                patient_id: list(
                    generator.get_patient_data_for_population_condition(patient_id)
                )
                for patient_id in range(batch_start, batch_start + self.batch_size)
            }
            database.setup(*patient_batch.values())
            results = engine.get_results(population_query)
            # Accumulate all data from matching patients, returning once we have enough
            for row in results:
                data.extend(patient_batch[row.patient_id])
                # Include additional data needed for the dataset but not required just
                # to determine population membership
                data.extend(generator.get_remaining_patient_data(row.patient_id))
                found += 1
                if found >= self.population_size:
                    break

            log.info(
                f"Generated {batch_start + self.batch_size - 1} patients, "
                f"found {found} matching"
            )

            if found >= self.population_size:
                return data

            if time.time() - start > self.timeout:
                log.warn(
                    f"Failed to find {self.population_size} matching patients within "
                    f"{self.timeout} seconds — giving up"
                )
                # If we failed to generate any matching patients at all then generate an
                # empty instance of each table so we have _something_ to return. This
                # means that we get an empty dataset rather than an error, and can
                # create empty CSV tables with the right headers.
                if not data:
                    data = generator.get_one_empty_row_for_each_table()
                return data

        # Keep coverage happy: the loop should never complete
        assert False

    def get_results(self):
        database = InMemoryDatabase()
        database.setup(self.get_data())
        engine = InMemoryQueryEngine(database)
        return engine.get_results(self.variable_definitions)


class DummyPatientGenerator:
    def __init__(self, variable_definitions, random_seed):
        # TODO: I dislike using today's date as part of the data generation because it
        # makes the results non-deterministic. However until we're able to infer a
        # suitable time range by inspecting the query, this will have to do.
        self.today = date.today()
        self.rnd = random.Random()
        self.random_seed = random_seed

        self.query_info = QueryInfo.from_variable_definitions(variable_definitions)
        # Create ORM classes for each of the tables used in the dataset definition
        self.orm_classes = orm_classes_from_tables(
            table_info.get_table_node()
            for table_info in self.query_info.tables.values()
        )

    def get_patient_data_for_population_condition(self, patient_id):
        # Generate data for just those tables needed for determining whether the patient
        # is included in the population
        return self.get_patient_data(patient_id, self.query_info.population_table_names)

    def get_remaining_patient_data(self, patient_id):
        # Generate data for any tables not included above
        return self.get_patient_data(patient_id, self.query_info.other_table_names)

    def get_patient_data(self, patient_id, table_names):
        # Seed the random generator using the patient_id so we always generate the same
        # data for the same patient
        self.rnd.seed(f"{self.random_seed}:{patient_id}")
        # Generate some basic demographic facts about the patient which subsequent table
        # generators can use to ensure a consistent patient history
        self.generate_patient_facts()
        for name in table_names:
            # Seed the random generator per-table, so that we get the same data no
            # matter what order the tables are generated in
            self.rnd.seed(f"{self.random_seed}:{patient_id}:{name}")
            table_info = self.query_info.tables[name]
            # Support specialised generators for individual tables, otherwise just make
            # some empty rows
            get_rows = getattr(self, f"rows_for_{table_info.name}", self.empty_rows)
            rows = get_rows(table_info)
            for row in rows:
                # Fill in any values that haven't already been set by a specialised
                # generator
                self.populate_row(table_info, row)
                row["patient_id"] = patient_id
            orm_class = self.orm_classes[table_info.name]
            yield from (orm_class(**row) for row in rows)

    def generate_patient_facts(self):
        # TODO: We could obviously generate more realistic age distributions than this
        date_of_birth = self.today - timedelta(days=self.rnd.randrange(0, 120 * 365))
        age_days = self.rnd.randrange(105 * 365)
        date_of_death = date_of_birth + timedelta(days=age_days)

        self.date_of_birth = date_of_birth
        self.date_of_death = date_of_death if date_of_death < self.today else None
        self.events_start = self.date_of_birth
        self.events_end = min(self.today, date_of_death)

    def rows_for_patients(self, table_info):
        row = {
            "date_of_birth": self.date_of_birth,
            "date_of_death": self.date_of_death,
        }
        # Apply any FirstOfMonth constraints
        for key, value in row.items():
            if key in table_info.columns and value is not None:
                if table_info.columns[key].get_constraint(Constraint.FirstOfMonth):
                    row[key] = value.replace(day=1)
        return [row]

    def rows_for_practice_registrations(self, table_info):
        # TODO: Generate more interesting registration histories; for now, we just
        # assume that every patient is permanently registered with a single practice
        # from birth
        row = {
            "start_date": self.events_start,
            "end_date": None,
        }
        return [row]

    def empty_rows(self, table_info):
        # Generate a small handful of events for event-level tables
        max_rows = 1 if table_info.has_one_row_per_patient else 16
        row_count = self.rnd.randrange(max_rows + 1)
        return [{} for _ in range(row_count)]

    def populate_row(self, table_info, row):
        # Remove any columns created by table generators that aren't used in the query
        for extra_column in row.keys() - table_info.columns:
            del row[extra_column]
        # Populate any columns used in the query which haven't already been set
        for name, column_info in table_info.columns.items():
            if name not in row:
                row[name] = self.get_random_value(column_info)

    def get_random_value(self, column_info):
        # TODO: This never returns None although for realism it sometimes should
        if cat_constraint := column_info.get_constraint(Constraint.Categorical):
            # TODO: It's obviously not true in general that categories are equiprobable
            return self.rnd.choice(cat_constraint.values)
        elif column_info.values_used:
            if self.rnd.randint(0, len(column_info.values_used)) != 0:
                return self.rnd.choice(column_info.values_used)
        elif column_info.type is bool:
            return self.rnd.choice((True, False))
        elif column_info.type is int:
            # TODO: This distributon is obviously ridiculous but will do for now
            return self.rnd.randrange(100)
        elif column_info.type is float:
            # TODO: As is this
            return self.rnd.random() * 100
        elif column_info.type is str:
            # If the column must match a regex then generate matching strings
            if regex_constraint := column_info.get_constraint(Constraint.Regex):
                generator = get_regex_generator(regex_constraint.regex)
                return generator(self.rnd)
            # A random ASCII string is unlikely to be very useful here, but it at least
            # makes it a bit clearer what the issue is (that we don't know enough about
            # the column to generate anything more helpful) rather than the blank string
            # we always used to return
            return "".join(
                self.rnd.choice(CHARS) for _ in range(self.rnd.randrange(16))
            )
        elif column_info.type is date:
            # Use an exponential distribution to preferentially generate recent events
            # (mean of one year ago). This works OK for the our immediate purposes but
            # we'll no doubt have to iterate on this.
            days_ago = int(self.rnd.expovariate(1 / 365))
            event_date = self.events_end - timedelta(days=days_ago)
            # Clip to the available time range
            event_date = max(event_date, self.events_start)
            # Apply any FirstOfMonth constraints
            if column_info.get_constraint(Constraint.FirstOfMonth):
                event_date = event_date.replace(day=1)
            return event_date
        else:
            assert False, f"Unhandled type: {column_info.type}"

    def get_one_empty_row_for_each_table(self):
        # Useful if we can't generate any matching patients at all but we want to be
        # able to at least show the structure of each table
        return [orm_class(patient_id=1) for orm_class in self.orm_classes.values()]

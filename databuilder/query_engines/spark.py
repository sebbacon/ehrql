import datetime
import secrets

import sqlalchemy
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import ClauseElement, Executable, type_coerce

from .. import sqlalchemy_types
from .base_sql import BaseSQLQueryEngine
from .spark_dialect import SparkDialect


class CreateViewAs(Executable, ClauseElement):
    def __init__(self, name, query):
        self.name = name
        self.query = query

    def __str__(self):
        return str(self.query)


@compiles(CreateViewAs, "spark")
def _create_table_as(element, compiler, **kw):
    return "CREATE TEMPORARY VIEW {} AS {}".format(
        element.name,
        compiler.process(element.query),
    )


class SparkQueryEngine(BaseSQLQueryEngine):
    sqlalchemy_dialect = SparkDialect

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create a unique prefix for temporary tables. Including the date makes it
        # easier to clean this up by hand later if we have to.
        self.temp_table_prefix = "tmp_{today}_{random}_".format(
            today=datetime.date.today().strftime("%Y%m%d"),
            random=secrets.token_hex(6),
        )

    def write_query_to_table(self, table, query):
        """
        Returns a new query which, when executed, writes the results of `query`
        into `table`
        """
        return CreateViewAs(table.name, query)

    def get_temp_database(self):
        return self.backend.temporary_database

    def round_to_first_of_month(self, date):
        date = type_coerce(date, sqlalchemy_types.Date())

        first_of_month = sqlalchemy.func.date_trunc(
            "MONTH",
            date,
        )
        return type_coerce(first_of_month, sqlalchemy_types.Date())

    def round_to_first_of_year(self, date):
        date = type_coerce(date, sqlalchemy_types.Date())

        first_of_year = sqlalchemy.func.date_trunc(
            "YEAR",
            date,
        )

        return type_coerce(first_of_year, sqlalchemy_types.Date())
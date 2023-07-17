import importlib
import os
import sys
import warnings
from argparse import ArgumentParser, ArgumentTypeError
from pathlib import Path

from ehrql import __version__
from ehrql.file_formats import FILE_FORMATS, get_file_extension
from ehrql.utils.log_utils import init_logging
from ehrql.utils.string_utils import strip_indent

from .main import (
    CommandError,
    assure,
    create_dummy_tables,
    dump_dataset_sql,
    dump_example_data,
    generate_dataset,
    generate_measures,
    run_sandbox,
    test_connection,
)


QUERY_ENGINE_ALIASES = {
    "mssql": "ehrql.query_engines.mssql.MSSQLQueryEngine",
    "sqlite": "ehrql.query_engines.sqlite.SQLiteQueryEngine",
    "csv": "ehrql.query_engines.csv.CSVQueryEngine",
}


BACKEND_ALIASES = {
    "emis": "ehrql.backends.emis.EMISBackend",
    "tpp": "ehrql.backends.tpp.TPPBackend",
}


if not os.environ.get("PYTHONHASHSEED") == "0":  # pragma: no cover
    # The kinds of DoS attacks hash seed randomisation is designed to protect against
    # don't apply to ehrQL, and having consistent output makes debugging much easier
    warnings.warn(
        "PYTHONHASHSEED environment variable not set to 0, so generated SQL may not"
        " exactly match what is generated in production."
    )


def entrypoint():
    # This is covered by the Docker tests but they're not recorded for coverage
    return main(sys.argv[1:], environ=os.environ)  # pragma: no cover


def main(args, environ=None):
    environ = environ or {}

    # We allow users to pass arbitrary arguments to dataset definition modules, but they
    # must be seperated from any ehrql arguments by the string `--`
    if "--" in args:
        user_args = args[args.index("--") + 1 :]
        args = args[: args.index("--")]
    else:
        user_args = []

    parser = create_parser(user_args, environ)

    init_logging()

    kwargs = vars(parser.parse_args(args))
    function = kwargs.pop("function")

    try:
        function(**kwargs)
    except CommandError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


def create_parser(user_args, environ):
    parser = ArgumentParser(prog="ehrql", description="Generate datasets in OpenSAFELY")

    def show_help(**kwargs):
        parser.print_help()
        parser.exit()

    parser.set_defaults(function=show_help)
    parser.add_argument("--version", action="version", version=f"ehrql {__version__}")

    subparsers = parser.add_subparsers(help="sub-command help")
    add_generate_dataset(subparsers, environ, user_args)
    add_generate_measures(subparsers, environ, user_args)
    add_run_sandbox(subparsers, environ, user_args)
    add_dump_example_data(subparsers, environ, user_args)
    add_dump_dataset_sql(subparsers, environ, user_args)
    add_create_dummy_tables(subparsers, environ, user_args)
    add_assure(subparsers, environ, user_args)
    add_test_connection(subparsers, environ, user_args)

    return parser


def add_generate_dataset(subparsers, environ, user_args):
    parser = subparsers.add_parser("generate-dataset", help="Generate a dataset")
    parser.set_defaults(function=generate_dataset)
    parser.set_defaults(environ=environ)
    parser.set_defaults(user_args=user_args)
    parser.add_argument(
        "--output",
        help=(
            f"Path of the file where the dataset will be written (console by default),"
            f" supported formats: {', '.join(FILE_FORMATS)}"
        ),
        type=valid_output_path,
        dest="dataset_file",
    )
    add_dummy_data_file_argument(parser, environ)
    add_dummy_tables_argument(parser, environ)
    add_dataset_definition_file_argument(parser, environ)
    internal_args = create_internal_argument_group(parser, environ)
    add_dsn_argument(internal_args, environ)
    add_query_engine_argument(internal_args, environ)
    add_backend_argument(internal_args, environ)


def add_dump_dataset_sql(subparsers, environ, user_args):
    parser = subparsers.add_parser(
        "dump-dataset-sql",
        help=(
            "Output the SQL that would be executed to fetch the results of the "
            "dataset definition"
        ),
    )
    parser.set_defaults(function=dump_dataset_sql)
    parser.set_defaults(environ=environ)
    parser.set_defaults(user_args=user_args)
    parser.add_argument(
        "--output",
        help="SQL output file (outputs to console by default)",
        type=Path,
        dest="output_file",
    )
    add_dataset_definition_file_argument(parser, environ)
    add_query_engine_argument(parser, environ)
    add_backend_argument(parser, environ)


def add_create_dummy_tables(subparsers, environ, user_args):
    parser = subparsers.add_parser(
        "create-dummy-tables",
        help=("Write dummy data tables as CSV ready for customisation"),
    )
    parser.set_defaults(function=create_dummy_tables)
    parser.set_defaults(user_args=user_args)
    add_dataset_definition_file_argument(parser, environ)
    parser.add_argument(
        "dummy_tables_path",
        help=("Path to directory where CSV files (one per table) will be written"),
        type=Path,
    )


def add_generate_measures(subparsers, environ, user_args):
    parser = subparsers.add_parser("generate-measures", help="Generate measures")
    parser.set_defaults(function=generate_measures)
    parser.set_defaults(environ=environ)
    parser.set_defaults(user_args=user_args)
    parser.add_argument(
        "--output",
        help=(
            f"Path of the file where the measures will be written (console by default),"
            f" supported formats: {', '.join(FILE_FORMATS)}"
        ),
        type=valid_output_path,
        dest="output_file",
    )
    add_dummy_tables_argument(parser, environ)
    add_dummy_data_file_argument(parser, environ)
    parser.add_argument(
        "definition_file",
        help="Path of the file where measures are defined",
        type=existing_python_file,
    )
    internal_args = create_internal_argument_group(parser, environ)
    add_dsn_argument(internal_args, environ)
    add_query_engine_argument(internal_args, environ)
    add_backend_argument(internal_args, environ)


def add_run_sandbox(subparsers, environ, user_args):
    parser = subparsers.add_parser("sandbox", help="start ehrQL sandbox environment")
    parser.set_defaults(function=run_sandbox)
    parser.set_defaults(environ=environ)
    parser.add_argument(
        "dummy_tables_path",
        help="Path to directory of CSV files (one per table)",
        type=existing_directory,
    )


def add_assure(subparsers, environ, user_args):
    parser = subparsers.add_parser("assure", help="experimental")
    parser.set_defaults(function=assure)
    parser.set_defaults(environ=environ)
    parser.set_defaults(user_args=user_args)
    parser.add_argument(
        "test_data_file",
        help="The path of the file where the test data is defined",
        type=existing_python_file,
    )


def add_test_connection(subparsers, environ, user_args):
    parser = subparsers.add_parser(
        "test-connection", help="test the database connection configuration"
    )
    parser.set_defaults(function=test_connection)
    parser.set_defaults(environ=environ)
    parser.add_argument(
        "--backend",
        "-b",
        help="backend type to test",
        type=backend_from_id,
        default=environ.get("BACKEND", environ.get("OPENSAFELY_BACKEND")),
        dest="backend_class",
    )
    parser.add_argument(
        "--url",
        "-u",
        help="db url",
        default=environ.get("DATABASE_URL"),
    )


def add_dump_example_data(subparsers, environ, user_args):
    parser = subparsers.add_parser(
        "dump-example-data", help="dump example data to directory"
    )
    parser.set_defaults(function=dump_example_data)
    parser.set_defaults(environ=environ)


def create_internal_argument_group(parser, environ):
    return parser.add_argument_group(
        title="Internal Arguments",
        description=strip_indent(
            """
            You should not normally need to use these arguments: they are for the
            internal operation of ehrQL and the OpenSAFELY platform.
            """
        ),
    )


def add_dataset_definition_file_argument(parser, environ):
    parser.add_argument(
        "definition_file",
        help="The path of the file where the dataset is defined",
        type=existing_python_file,
        metavar="dataset_definition",
    )


def add_dsn_argument(parser, environ):
    parser.add_argument(
        "--dsn",
        help="Data Source Name: URL of remote database, or path to data on disk",
        type=str,
        default=environ.get("DATABASE_URL"),
    )


def add_dummy_data_file_argument(parser, environ):
    parser.add_argument(
        "--dummy-data-file",
        help="Provide dummy data from a file to be validated and used as the output",
        type=existing_file,
    )


def add_dummy_tables_argument(parser, environ):
    parser.add_argument(
        "--dummy-tables",
        help=(
            "Path to directory of CSV files (one per table) to use when generating "
            "dummy data"
        ),
        type=existing_directory,
        dest="dummy_tables_path",
    )


def add_query_engine_argument(parser, environ):
    parser.add_argument(
        "--query-engine",
        type=query_engine_from_id,
        help=f"Dotted import path to class, or one of: {', '.join(QUERY_ENGINE_ALIASES)}",
        default=environ.get("OPENSAFELY_QUERY_ENGINE"),
        dest="query_engine_class",
    )


def add_backend_argument(parser, environ):
    parser.add_argument(
        "--backend",
        type=backend_from_id,
        help=f"Dotted import path to class, or one of: {', '.join(BACKEND_ALIASES)}",
        default=environ.get("OPENSAFELY_BACKEND"),
        dest="backend_class",
    )


def existing_file(value):
    path = Path(value)
    if not path.exists():
        raise ArgumentTypeError(f"{value} does not exist")
    if not path.is_file():
        raise ArgumentTypeError(f"{value} is not a file")
    return path


def existing_directory(value):
    path = Path(value)
    if not path.exists():
        raise ArgumentTypeError(f"{value} does not exist")
    if not path.is_dir():
        raise ArgumentTypeError(f"{value} is not a directory")
    return path


def existing_python_file(value):
    path = Path(value)
    if not path.exists():
        raise ArgumentTypeError(f"{value} does not exist")
    if not path.suffix == ".py":
        raise ArgumentTypeError(f"{value} is not a Python file")
    return path


def valid_output_path(value):
    path = Path(value)
    extension = get_file_extension(path)
    if extension not in FILE_FORMATS:
        raise ArgumentTypeError(
            f"'{extension}' is not a supported format, must be one of: "
            f"{', '.join(FILE_FORMATS)}"
        )
    return path


def query_engine_from_id(str_id):
    if "." not in str_id:
        try:
            str_id = QUERY_ENGINE_ALIASES[str_id]
        except KeyError:
            raise ArgumentTypeError(
                f"must be one of: {', '.join(QUERY_ENGINE_ALIASES.keys())} "
                f"(or a full dotted path to a query engine class)"
            )
    query_engine = import_string(str_id)
    assert_duck_type(query_engine, "query engine", "get_results")
    return query_engine


def backend_from_id(str_id):
    # Workaround for the fact that Job Runner insists on setting OPENSAFELY_BACKEND to
    # "expectations" when running locally. Cohort Extractor backends have a different
    # meaning from ehrQL's, and the semantics of the "expectations" backend
    # translate to "no backend at all" in ehrQL terms so that's how we treat it.
    if str_id == "expectations":
        return None

    if "." not in str_id:
        try:
            str_id = BACKEND_ALIASES[str_id]
        except KeyError:
            raise ArgumentTypeError(
                f"(or OPENSAFELY_BACKEND) must be one of: {', '.join(BACKEND_ALIASES.keys())} "
                f"(or a full dotted path to a backend class) but got '{str_id}'"
            )
    backend = import_string(str_id)
    assert_duck_type(backend, "backend", "get_table_expression")
    return backend


def import_string(dotted_path):
    if "." not in dotted_path:
        raise ArgumentTypeError("must be a full dotted path to a Python class")
    module_name, _, attribute_name = dotted_path.rpartition(".")
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        raise ArgumentTypeError(f"could not import module '{module_name}'")
    try:
        return getattr(module, attribute_name)
    except AttributeError:
        raise ArgumentTypeError(
            f"module '{module_name}' has no attribute '{attribute_name}'"
        )


def assert_duck_type(obj, type_name, required_method):
    if not hasattr(obj, required_method):
        raise ArgumentTypeError(
            f"{obj} is not a valid {type_name}: no '{required_method}' method"
        )


if __name__ == "__main__":
    entrypoint()

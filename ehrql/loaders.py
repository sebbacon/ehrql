import importlib.util
import os
import subprocess
import sys

from ehrql.measures import Measures
from ehrql.query_language import Dataset, compile
from ehrql.serializer import deserialize
from ehrql.utils.traceback_utils import get_trimmed_traceback


class DefinitionError(Exception):
    "Error in or with the user-supplied definition file"


def load_dataset_definition(definition_file, user_args):
    return load_definition_in_subprocess("dataset", definition_file, user_args)


def load_measure_definitions(definition_file, user_args):
    return load_definition_in_subprocess("measures", definition_file, user_args)


def load_test_definition(definition_file, user_args):
    return load_definition_in_subprocess("test", definition_file, user_args)


def load_definition_in_subprocess(definition_type, definition_file, user_args):
    # NOTE: This is not yet safe because the subprocess needs to be isolated to prevent
    # it doing things like accessing the network, but it is the first step towards that
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ehrql",
            "serialize-definition",
            "--definition-type",
            definition_type,
            definition_file,
            "--",
            *user_args,
        ],
        env={
            # Our Docker image relies on PYTHONPATH to make the ehrql package available
            "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
            # Our entrypoint will emit warnings if we don't set this
            "PYTHONHASHSEED": "0",
        },
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise DefinitionError(result.stderr)
    else:
        # Pass through any warnings or logs generated by the subprocess
        print(result.stderr, file=sys.stderr, end="")
    return deserialize(result.stdout)


# The `_unsafe` functions below are so named because they import user-supplied code
# directly into the running process. They should therefore only be run in either an
# isolated subprocess, or in local/test contexts.


def load_dataset_definition_unsafe(definition_file, user_args):
    module = load_module(definition_file, user_args)
    variable_definitions = get_variable_definitions_from_module(module)
    return variable_definitions, module.dataset.dummy_data_config


def load_test_definition_unsafe(definition_file, user_args):
    module = load_module(definition_file, user_args)
    variable_definitions = get_variable_definitions_from_module(module)
    return variable_definitions, module.patient_data


def get_variable_definitions_from_module(module):
    try:
        dataset = module.dataset
    except AttributeError:
        raise DefinitionError(
            "Did not find a variable called 'dataset' in dataset definition file"
        )
    if not isinstance(dataset, Dataset):
        raise DefinitionError("'dataset' must be an instance of ehrql.Dataset")
    if not hasattr(dataset, "population"):
        raise DefinitionError(
            "A population has not been defined; define one with define_population()"
        )
    return compile(dataset)


def load_measure_definitions_unsafe(definition_file, user_args):
    module = load_module(definition_file, user_args)
    try:
        measures = module.measures
    except AttributeError:
        raise DefinitionError(
            "Did not find a variable called 'measures' in measures definition file"
        )
    if not isinstance(measures, Measures):
        raise DefinitionError("'measures' must be an instance of ehrql.Measures")
    if len(measures) == 0:
        raise DefinitionError("No measures defined")
    return list(measures)


DEFINITION_LOADERS = {
    "dataset": load_dataset_definition_unsafe,
    "measures": load_measure_definitions_unsafe,
    "test": load_test_definition_unsafe,
}


def load_definition_unsafe(definition_type, definition_file, user_args):
    return DEFINITION_LOADERS[definition_type](definition_file, user_args)


def load_module(module_path, user_args=()):
    # Taken from the official recipe for importing a module from a file path:
    # https://docs.python.org/3.9/library/importlib.html#importing-a-source-file-directly
    spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
    module = importlib.util.module_from_spec(spec)
    # Temporarily add the directory containing the definition to the start of `sys.path`
    # (just as `python path/to/script.py` would) so that the definition can import
    # library modules from that directory
    original_sys_path = sys.path.copy()
    sys.path.insert(0, str(module_path.parent.absolute()))
    # Temporarily modify `sys.argv` so it contains any user-supplied arguments and
    # generally looks as it would had you run: `python script.py some args --here`
    original_sys_argv = sys.argv.copy()
    sys.argv = [str(module_path), *user_args]
    try:
        spec.loader.exec_module(module)
        return module
    except Exception as exc:
        traceback = get_trimmed_traceback(exc, module.__file__)
        raise DefinitionError(f"Failed to import '{module_path}':\n\n{traceback}")
    finally:
        sys.path = original_sys_path
        sys.argv = original_sys_argv

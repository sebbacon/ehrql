# just has no idiom for setting a default value for an environment variable
# so we shell out, as we need VIRTUAL_ENV in the justfile environment
export VIRTUAL_ENV  := `echo ${VIRTUAL_ENV:-.venv}`

# TODO: make it /scripts on windows?
export BIN := VIRTUAL_ENV + "/bin"
export PIP := BIN + "/python -m pip"
# enforce our chosen pip compile flags
export COMPILE := BIN + "/pip-compile --allow-unsafe --generate-hashes"


alias help := list

# list available commands
list:
    @just --list


# clean up temporary files
clean:
    rm -rf .venv  # default just-managed venv

# ensure valid virtualenv
_virtualenv:
    #!/usr/bin/env bash
    # allow users to specify python version in .env
    PYTHON_VERSION=${PYTHON_VERSION:-python3.9}

    # create venv and upgrade pip
    test -d $VIRTUAL_ENV || { $PYTHON_VERSION -m venv $VIRTUAL_ENV && $PIP install --upgrade pip; }

    # ensure we have pip-tools so we can run pip-compile
    test -e $BIN/pip-compile || $PIP install pip-tools


# update requirements.prod.txt if requirement.prod.in has changed
requirements-prod: _virtualenv
    #!/usr/bin/env bash
    # exit if .in file is older than .txt file (-nt = 'newer than', but we negate with || to avoid error exit code)
    test requirements.prod.in -nt requirements.prod.txt || exit 0
    $COMPILE --output-file=requirements.prod.txt requirements.prod.in


# update requirements.dev.txt if requirements.dev.in has changed
requirements-dev: requirements-prod
    #!/usr/bin/env bash
    # exit if .in file is older than .txt file (-nt = 'newer than', but we negate with || to avoid error exit code)
    test requirements.dev.in -nt requirements.dev.txt || exit 0
    $COMPILE --output-file=requirements.dev.txt requirements.dev.in


# ensure prod requirements installed and up to date
prodenv: requirements-prod
    #!/usr/bin/env bash
    # exit if .txt file has not changed since we installed them (-nt == "newer than', but we negate with || to avoid error exit code)
    test requirements.prod.txt -nt $VIRTUAL_ENV/.prod || exit 0

    $PIP install -r requirements.prod.txt
    touch $VIRTUAL_ENV/.prod


# && dependencies are run after the recipe has run. Needs just>=0.9.9. This is
# a killer feature over Makefiles.
#
# ensure dev requirements installed and up to date
devenv: prodenv requirements-dev && _install-precommit
    #!/usr/bin/env bash
    # exit if .txt file has not changed since we installed them (-nt == "newer than', but we negate with || to avoid error exit code)
    test requirements.dev.txt -nt $VIRTUAL_ENV/.dev || exit 0

    $PIP install -r requirements.dev.txt
    touch $VIRTUAL_ENV/.dev


# ensure precommit is installed
_install-precommit:
    #!/usr/bin/env bash
    BASE_DIR=$(git rev-parse --show-toplevel)
    test -f $BASE_DIR/.git/hooks/pre-commit || $BIN/pre-commit install


# upgrade dev or prod dependencies (all by default, specify package to upgrade single package)
upgrade env package="": _virtualenv
    #!/usr/bin/env bash
    opts="--upgrade"
    test -z "{{ package }}" || opts="--upgrade-package {{ package }}"
    $COMPILE $opts --output-file=requirements.{{ env }}.txt requirements.{{ env }}.in

# runs the format (black), sort (isort) and lint (flake8) checks but does not change any files
check: devenv
    $BIN/black --check .
    $BIN/isort --check-only --diff .
    $BIN/flake8


# runs the format (black) and sort (isort) checks and fixes the files
fix: devenv
    $BIN/black .
    $BIN/isort .


# build the cohort-extractor docker image
build-cohort-extractor:
    #!/usr/bin/env bash
    set -euo pipefail

    [[ -v CI ]] && echo "::group::Build cohort-extractor (click to view)" || echo "Build cohort-extractor"
    docker build . -t cohort-extractor-v2
    [[ -v CI ]] && echo "::endgroup::" || echo ""


# tear down the persistent cohort-extractor-mssql docker container and network
remove-persistent-database:
    docker rm --force cohort-extractor-mssql
    docker network rm cohort-extractor-network

# open an interactive SQL Server shell running against the persistent database
connect-to-persistent-database:
    docker exec -it cohort-extractor-mssql /opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P 'Your_password123!'

# Full set of tests run by CI
test: test-all

# run the unit tests only. Optional args are passed to pytest
test-unit *ARGS: devenv
    $BIN/python -m pytest -m "not integration and not smoke" {{ ARGS }}

# run the integration tests only. Optional args are passed to pytest
test-integration *ARGS: devenv
    $BIN/python -m pytest -m integration {{ ARGS }}

# run the smoke tests only. Optional args are passed to pytest
test-smoke *ARGS: devenv build-cohort-extractor
    $BIN/python -m pytest -m smoke {{ ARGS }}

# run all tests including integration and smoke tests. Optional args are passed to pytest
test-all *ARGS: devenv build-cohort-extractor
    #!/usr/bin/env bash
    set -euo pipefail

    [[ -v CI ]] && echo "::group::Run tests (click to view)" || echo "Run tests"
    $BIN/python -m pytest --cov=cohortextractor --cov=tests {{ ARGS }}
    [[ -v CI ]]  && echo "::endgroup::" || echo ""

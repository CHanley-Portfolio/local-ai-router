# Local AI Router — Project Structure

## Overview

The Local AI Router is structured as a standard installable Python project using a `src/` layout.

The project is packaged through `pyproject.toml` and installed into the development virtual environment using an editable installation.

This structure prevents the application from depending on working-directory import behavior and makes development, testing, and future deployment more reproducible.

## Repository structure

```text
local-ai-router/
├── pyproject.toml
├── requirements.lock.txt
├── requirements-dev.lock.txt
├── docs/
│   ├── project_structure.md
│   └── routing_policy_v1.md
├── src/
│   └── local_ai_router/
│       ├── __init__.py
│       ├── config.py
│       ├── main.py
│       ├── ollama_client.py
│       ├── routing.py
│       └── schemas.py
└── tests/
    ├── test_chat_api.py
    ├── test_route_api.py
    └── test_routing.py
```

## `pyproject.toml`

`pyproject.toml` is the primary project configuration file.

It defines:

* project name and version;
* supported Python version;
* runtime dependencies;
* development dependencies;
* setuptools build configuration;
* the `src/` package layout;
* pytest configuration.

Direct dependency declarations should be maintained in this file rather than duplicated across separate input files.

## Source layout

Application code is stored under:

```text
src/local_ai_router/
```

The distribution name is:

```text
local-ai-router
```

The Python import package is:

```python
import local_ai_router
```

The hyphenated distribution name and underscored Python package name serve different purposes and are intentionally different.

Using a `src/` layout helps ensure tests and applications use the installed package rather than accidentally importing source files directly from the repository root.

## Editable development installation

During development, the package is installed using:

```bash
python -m pip install -e ".[dev]"
```

The `-e` option performs an editable installation.

This means the virtual environment references the source code under:

```text
src/local_ai_router/
```

rather than copying a fixed version of the source into the virtual environment.

Changes made to the Python source are therefore immediately visible without reinstalling the project after every edit.

## Runtime dependencies

Runtime dependencies are declared under:

```toml
[project]
dependencies = [...]
```

These are packages required for the Local AI Router itself to operate.

Current major runtime dependencies include:

* FastAPI;
* HTTPX.

Transitive dependencies are resolved from those direct dependencies.

## Development dependencies

Development-only tools are declared under:

```toml
[project.optional-dependencies]
dev = [...]
```

Current development tools include:

* pytest;
* pip-tools.

These tools are needed to develop, test, and maintain the project but are not fundamental runtime requirements of the router.

## Dependency lock files

Two lock files preserve exact dependency versions.

### `requirements.lock.txt`

Contains the resolved runtime dependency environment.

It is generated from `pyproject.toml`.

### `requirements-dev.lock.txt`

Contains the resolved development environment, including the `dev` dependency group.

It is also generated from `pyproject.toml`.

The lock files allow a known dependency environment to be reproduced instead of resolving potentially newer package versions every time the project is installed.

## Regenerating lock files

Runtime dependencies:

```bash
python -m piptools compile pyproject.toml \
  --strip-extras \
  --output-file requirements.lock.txt
```

Development dependencies:

```bash
python -m piptools compile pyproject.toml \
  --extra dev \
  --strip-extras \
  --output-file requirements-dev.lock.txt
```

Direct dependencies should first be changed in `pyproject.toml`.

The lock files should then be regenerated rather than edited manually.

## Reproducing the development environment

A clean development environment can be created with:

```bash
python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements-dev.lock.txt
python -m pip install -e . --no-deps
```

The lock file installs the exact dependency versions.

The final command installs the Local AI Router itself as an editable package without asking pip to resolve the dependency graph again.

Dependency consistency can be verified with:

```bash
python -m pip check
```

## Testing

Pytest configuration now lives inside `pyproject.toml`.

The complete automated suite can be run with:

```bash
python -m pytest -v
```

The project does not require a `PYTHONPATH=src` environment variable or a pytest-specific Python-path workaround.

This is intentional: tests should exercise the installed package in the same way other Python code would import it.

## Packaging verification

The packaging configuration has been validated using a separate clean virtual environment.

The validation confirmed that:

* exact development dependencies could be installed from the lock file;
* `pip check` reported no broken requirements;
* `local_ai_router` imported from the editable project installation;
* pytest discovered configuration from `pyproject.toml`;
* all 12 automated tests passed.

This clean-environment test demonstrates that the development setup is reproducible without relying on the original development virtual environment.

## Design rationale

The project originally used:

```text
pythonpath = src
```

inside `pytest.ini` to make the source package importable during testing.

That approach was useful during early development but tied successful imports to pytest configuration.

The project now uses standard Python packaging instead.

This gives the repository a clearer boundary:

```text
source code
    ↓
installable Python package
    ↓
application / tests / future services
```

That structure is more suitable for continued development, automated CI, deployment, and portfolio review.

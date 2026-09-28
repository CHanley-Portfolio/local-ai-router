# Local AI Router — Project Structure

## Overview

The Local AI Router is structured as a standard installable Python project using a `src/` layout.

The project is packaged through `pyproject.toml` and installed into the development virtual environment using an editable installation.

This structure prevents the application from depending on working-directory import behavior and makes development, testing, database migrations, benchmarking, and future deployment more reproducible.

The architecture is deliberately divided into separate concerns:

- HTTP/API orchestration;
- routing policy;
- inference contracts;
- backend-specific inference adapters;
- PostgreSQL persistence;
- benchmark infrastructure;
- shared application data contracts;
- automated testing.

This separation is intended to keep the router maintainable as additional inference engines, benchmarking systems, retrieval, memory, tools, and frontend services are introduced.

---

## Repository structure

```text
local-ai-router/
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── benchmarks/
│   ├── datasets/
│   └── fixtures/
│
├── docs/
│   ├── benchmark_database_design_v1.md
│   ├── benchmark_methodology_v1.md
│   ├── external_benchmark_suite_v1.md
│   ├── project_structure.md
│   ├── routing_policy_v1.md
│   └── testing_and_ci.md
│
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── src/
│   └── local_ai_router/
│       ├── __init__.py
│       ├── config.py
│       ├── main.py
│       ├── ollama_client.py
│       ├── schemas.py
│       │
│       ├── inference/
│       │   ├── __init__.py
│       │   └── data/
│       │       ├── __init__.py
│       │       ├── inference_request.py
│       │       └── inference_result.py
│       │
│       ├── persistence/
│       │   ├── __init__.py
│       │   ├── database.py
│       │   └── benchmark/
│       │       ├── __init__.py
│       │       ├── base.py
│       │       ├── seeding.py
│       │       ├── models/
│       │       └── repositories/
│       │
│       └── routing/
│           ├── __init__.py
│           ├── router.py
│           └── data/
│
├── tests/
│   ├── test_benchmark_database_integration.py
│   ├── test_benchmark_dataset.py
│   ├── test_benchmark_models.py
│   ├── test_benchmark_persistence.py
│   ├── test_chat_api.py
│   ├── test_database.py
│   ├── test_inference_contracts.py
│   ├── test_route_api.py
│   ├── test_routing.py
│   └── test_routing_contracts.py
│
├── alembic.ini
├── pyproject.toml
├── requirements.lock.txt
└── requirements-dev.lock.txt
```

The exact file set will continue to evolve as the benchmark runner, model registry, frontend, retrieval system, and additional inference adapters are implemented.

---

## `pyproject.toml`

`pyproject.toml` is the primary project configuration file.

It defines:

- project name and version;
- supported Python version;
- runtime dependencies;
- development dependencies;
- setuptools build configuration;
- the `src/` package layout;
- pytest configuration;
- Ruff configuration;
- Alembic configuration.

Direct dependency declarations should be maintained in this file rather than duplicated across separate input files.

---

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

---

## Major application layers

The application is divided into several major responsibilities.

### `main.py`

`main.py` contains the FastAPI application and HTTP-facing orchestration.

Its responsibilities include:

- application startup and shutdown;
- API endpoint registration;
- request validation coordination;
- invoking routing logic;
- invoking inference adapters;
- translating application results into API responses.

`main.py` should not contain backend-specific inference parsing, database schema logic, or routing policy.

---

### `schemas.py`

`schemas.py` contains Pydantic request and response models used by FastAPI.

These schemas define the public HTTP contract exposed by the router.

API schemas are separate from internal data objects because the public HTTP interface and internal application contracts may evolve independently.

---

## Routing layer

Routing code is stored under:

```text
src/local_ai_router/routing/
```

The routing layer decides how a request should be handled.

Current shared routing fields include:

```text
route_mode
thinking_enabled
route_reason
```

Routing decisions are represented through explicit application data objects rather than loosely structured dictionaries.

Backend-specific inference behavior should not leak into the routing layer.

For example, the router understands:

```text
thinking_enabled
```

while Ollama currently expects:

```text
think
```

That translation is the responsibility of the inference adapter.

---

## Inference abstraction

Inference backends are isolated from the rest of the Local AI Router through application-level request and result contracts.

The stable application boundary is:

```text
API / benchmark runner / future services
                ↓
        InferenceRequest
                ↓
        inference adapter
                ↓
       backend-specific API

       backend-specific response
                ↓
        inference adapter
                ↓
         InferenceResult
                ↓
API / benchmark runner / future services
```

### `InferenceRequest`

`InferenceRequest` represents what the Local AI Router wants an inference backend to execute.

It currently supports fields such as:

```text
model_name
user_message
thinking_enabled
temperature
top_p
seed
max_output_tokens
backend_options
```

Higher-level application code constructs an `InferenceRequest` rather than manually building an Ollama request dictionary.

This keeps application code independent from the exact request format of the inference backend.

---

### `InferenceResult`

`InferenceResult` represents the normalized output of one inference operation.

It currently supports information such as:

```text
model_name
response_text
total_duration_ns
model_load_duration_ns
prompt_token_count
prompt_eval_duration_ns
output_token_count
output_eval_duration_ns
backend_metrics
```

Application layers consume this normalized representation rather than raw backend JSON.

---

## Ollama adapter

`ollama_client.py` currently implements the inference adapter for Ollama.

It is responsible for translating:

```text
InferenceRequest
        ↓
Ollama request JSON
```

and:

```text
Ollama response JSON
        ↓
InferenceResult
```

For example, Ollama currently uses native fields such as:

```text
think
eval_count
eval_duration
prompt_eval_count
prompt_eval_duration
load_duration
```

The rest of the Local AI Router instead uses normalized names such as:

```text
thinking_enabled
output_token_count
output_eval_duration_ns
prompt_token_count
prompt_eval_duration_ns
model_load_duration_ns
```

Backend-specific naming remains isolated inside the adapter.

This means a future backend such as llama.cpp, vLLM, another local runtime, or a remote inference service can implement the same application boundary without requiring the API, routing system, benchmark runner, or persistence layer to understand that backend's native protocol.

Conceptually:

```text
                         ┌─ OllamaClient ───── Ollama protocol
InferenceRequest ────────┤
                         ├─ FutureClient ───── another protocol
                         └─ FutureClient ───── another protocol

All adapters return:

InferenceResult
```

This backend-independence is an important architectural requirement for the benchmark system because benchmark logic should evaluate models rather than be permanently coupled to one inference engine.

---

## Persistence layer

Database infrastructure is stored under:

```text
src/local_ai_router/persistence/
```

Shared SQLAlchemy engine and session creation lives in:

```text
persistence/database.py
```

Database connection details are loaded from application configuration rather than being embedded inside ORM models or migration files.

This allows persistence classes and repositories to remain independent from credentials and local PostgreSQL connection details.

---

## Benchmark persistence

Benchmark persistence is isolated under:

```text
src/local_ai_router/persistence/benchmark/
```

The benchmark database uses a dedicated PostgreSQL schema:

```text
benchmark
```

The schema stores:

- model identities;
- model variants;
- quantizations;
- model inference profiles;
- benchmark definitions;
- benchmark categories;
- benchmark cases;
- tags;
- suites;
- hardware profiles;
- runtime profiles;
- context profiles;
- benchmark runs;
- individual case results;
- criterion-level quality scores;
- performance metrics;
- external reference results.

Historical benchmark executions are append-oriented.

New benchmark runs create new database records rather than replacing previous results.

This allows comparisons across:

- model versions;
- quantizations;
- configuration changes;
- router revisions;
- hardware changes;
- runtime changes;
- context strategies;
- benchmark suite versions.

---

## Database migrations

PostgreSQL schema changes are managed through Alembic.

Migration files are stored under:

```text
migrations/versions/
```

ORM models define the desired database structure, while Alembic migrations provide the version-controlled path for changing a real PostgreSQL database.

Database schema changes should not be applied manually through DBeaver when they belong to the application schema.

The expected workflow is:

```text
SQLAlchemy ORM change
        ↓
automated tests
        ↓
Alembic autogeneration
        ↓
migration inspection
        ↓
migration SQL preview
        ↓
database upgrade
```

DBeaver remains useful for:

- database administration;
- viewing schemas and tables;
- inspecting records;
- running diagnostic SQL;
- visualizing relationships.

---

## Benchmark seeding

Synthetic benchmark integration-test data is generated through:

```text
persistence/benchmark/seeding.py
```

Test seeding is deliberately restricted to:

```text
local_ai_router_test
```

The seed operation is idempotent.

Running it repeatedly reuses existing configuration rows instead of inserting duplicate models, suites, cases, or profiles.

Synthetic benchmark runs created during integration tests are executed inside transactions and rolled back after the test.

This keeps the test database predictable while preventing synthetic history from polluting real benchmark data.

---

## Runtime dependencies

Runtime dependencies are declared under:

```toml
[project]
dependencies = [...]
```

Current major runtime dependencies include:

- FastAPI;
- HTTPX;
- SQLAlchemy;
- Psycopg.

FastAPI provides the HTTP application framework.

HTTPX is used for HTTP communication with inference services such as Ollama.

SQLAlchemy provides ORM and database infrastructure.

Psycopg provides the PostgreSQL driver.

---

## Development dependencies

Development-only tools are declared under:

```toml
[project.optional-dependencies]
dev = [...]
```

Current development tools include:

- pytest;
- pip-tools;
- Ruff;
- Alembic.

These tools support development, testing, dependency locking, formatting, linting, and database migrations.

---

## Dependency lock files

Two lock files preserve exact dependency versions.

### `requirements.lock.txt`

Contains the resolved runtime dependency environment.

It is generated from `pyproject.toml`.

### `requirements-dev.lock.txt`

Contains the resolved development environment, including the `dev` dependency group.

It is also generated from `pyproject.toml`.

The lock files allow a known dependency environment to be reproduced instead of resolving potentially newer package versions every time the project is installed.

---

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

---

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

Changes made to Python source are therefore immediately visible without reinstalling the project after every edit.

---

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

---

## Testing

Pytest configuration lives inside `pyproject.toml`.

The complete automated suite can be run with:

```bash
python -m pytest -v
```

The project does not require:

```text
PYTHONPATH=src
```

or a pytest-specific source-path workaround.

Tests exercise the installed package in the same way other Python applications import it.

The test suite currently covers:

- routing behavior;
- routing contracts;
- API validation;
- mocked chat execution;
- normalized inference contracts;
- database configuration;
- benchmark dataset integrity;
- SQLAlchemy benchmark metadata;
- ORM relationship configuration;
- PostgreSQL benchmark integration;
- historical benchmark querying;
- idempotent seed support.

---

## Code-quality checks

Ruff is used for formatting and focused linting.

The normal local validation sequence is:

```bash
ruff format src tests migrations
ruff check src tests migrations
ruff format --check src tests migrations
python -m pytest -v
```

These checks should pass before significant changes are committed.

---

## Packaging verification

The packaging configuration has been validated using clean development environments.

Validation has confirmed that:

- locked development dependencies can be installed;
- `pip check` reports no broken requirements;
- `local_ai_router` imports from the editable project installation;
- pytest discovers configuration from `pyproject.toml`;
- the complete automated test suite passes in the configured development environment.

This demonstrates that development does not depend on hidden local import behavior.

---

## Design rationale

The project originally used:

```text
pythonpath = src
```

inside pytest configuration to make the source package importable during testing.

That approach was useful during early development but tied successful imports to pytest configuration.

The project now uses standard Python packaging instead.

The broader architecture has similarly evolved away from direct backend coupling.

The application now follows boundaries such as:

```text
HTTP request
    ↓
API schema
    ↓
routing
    ↓
InferenceRequest
    ↓
backend adapter
    ↓
inference backend
    ↓
InferenceResult
    ↓
API / benchmark / persistence
```

and:

```text
benchmark configuration
    ↓
benchmark execution
    ↓
normalized inference
    ↓
quality + performance evaluation
    ↓
PostgreSQL history
```

These boundaries reduce coupling and make the Local AI Router more suitable for:

- multiple model backends;
- automated benchmarking;
- model selection;
- regression analysis;
- retrieval;
- project-aware context;
- future tools and agents;
- frontend dashboards;
- portfolio review;
- deployment.

The goal is not simply to make the current implementation work.

The project structure is intended to support continued growth without requiring core systems to be rewritten each time a new capability is introduced.

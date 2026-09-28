# Local AI Router — Testing, CI, and Static Type-Checking Strategy

## Overview

The Local AI Router uses automated testing and code-quality checks to detect regressions as the project grows.

The development workflow is designed so the same core quality gates can be run both:

- locally before committing code;
- automatically through GitHub Actions after pushes and pull requests.

The test strategy deliberately separates:

- deterministic application tests;
- database integration tests;
- backend adapter tests;
- real model inference and benchmark execution.

Normal CI should remain fast and deterministic.

Tests that depend on a local GPU, Ollama installation, or downloaded models remain separate from routine GitHub-hosted CI.

---

## Current quality gates

The project currently uses several automated quality checks.

### Dependency consistency

```bash
python -m pip check
```

This verifies that installed package dependencies are internally compatible.

---

### Ruff linting

```bash
ruff check src tests migrations
```

Ruff currently checks:

- important Python syntax and style errors;
- undefined or invalid names;
- unused imports and related Pyflakes issues;
- import ordering.

The rule set is intentionally focused rather than enabling every available Ruff rule immediately.

Rules may become stricter as the codebase and conventions stabilize.

---

### Ruff formatting

```bash
ruff format --check src tests migrations
```

CI checks formatting but should not automatically modify repository files.

Formatting changes should be applied locally with:

```bash
ruff format src tests migrations
```

This keeps repository changes deliberate and reviewable.

---

### Automated tests

```bash
python -m pytest -v
```

The automated suite contains a combination of:

- unit tests;
- API tests;
- contract tests;
- SQLAlchemy metadata tests;
- ORM configuration tests;
- benchmark dataset tests;
- PostgreSQL integration tests.

Real GPU inference remains separate from the ordinary deterministic suite.

---

## GitHub Actions

The CI workflow is defined under:

```text
.github/workflows/
```

The workflow runs automatically for:

- repository pushes;
- pull requests.

The pipeline creates a clean GitHub-hosted environment, installs Python, installs locked development dependencies, installs the Local AI Router package, and executes the configured quality gates.

A CI failure therefore indicates that at least one required repository validation did not pass.

---

## Local development workflow

Before pushing significant changes, the primary local validation sequence is:

```bash
ruff format src tests migrations
ruff check src tests migrations
ruff format --check src tests migrations
python -m pytest -v
```

These checks intentionally mirror the important validations used by CI.

Supported Ruff fixes can be applied with:

```bash
ruff check --fix src tests migrations
```

Automatic fixes should still be reviewed before committing.

---

## Test categories

The test suite is divided by architectural responsibility.

### Unit tests

Unit tests validate isolated application behavior.

Examples include:

- routing decisions;
- routing data contracts;
- inference data contracts;
- configuration behavior.

These should not require external services.

---

### API tests

FastAPI tests validate HTTP-facing behavior.

Examples include:

- schema validation;
- routing metadata;
- default model selection;
- readable HTTP errors;
- behavior when inference services fail.

The real Ollama service is mocked in these tests.

This keeps the API suite:

- fast;
- deterministic;
- independent from GPU availability;
- independent from downloaded models;
- easier to debug.

---

## Inference-boundary testing

Inference tests deliberately distinguish between the application-level inference contract and backend-specific communication.

The normalized application boundary is:

```text
InferenceRequest
        ↓
inference adapter
        ↓
InferenceResult
```

API tests mock this normalized boundary.

They should not return raw Ollama response dictionaries because parsing Ollama's protocol is no longer the responsibility of the API layer.

For example, API tests now mock:

```python
InferenceResult(
    model_name="test-model",
    response_text="Example response",
    output_token_count=20,
)
```

rather than:

```python
{
    "model": "test-model",
    "message": {
        "content": "Example response"
    },
    "eval_count": 20,
}
```

This makes the test accurately represent the actual application architecture.

---

## Backend adapter testing

Backend-specific tests validate translation between normalized inference contracts and the native backend protocol.

For Ollama, the boundary is:

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

Adapter tests should verify translations such as:

| Ollama field | Local AI Router field |
| --- | --- |
| `think` | `thinking_enabled` |
| `eval_count` | `output_token_count` |
| `eval_duration` | `output_eval_duration_ns` |
| `prompt_eval_count` | `prompt_token_count` |
| `prompt_eval_duration` | `prompt_eval_duration_ns` |
| `load_duration` | `model_load_duration_ns` |
| `total_duration` | `total_duration_ns` |

This separation ensures that a failure in Ollama parsing is attributed to the Ollama adapter rather than producing unrelated API or benchmark failures.

Future inference adapters should receive their own equivalent translation tests.

---

## Centralized data contracts

Important application boundaries use shared typed data objects rather than backend-specific dictionaries or independently recreated structures.

Established contracts currently include:

- routing request modes;
- routing execution modes;
- routing decisions;
- `InferenceRequest`;
- `InferenceResult`.

The inference contracts form the stable boundary between application code and inference adapters.

Application layers such as:

- FastAPI;
- benchmark execution;
- future model selection;
- future agent workflows;

should not consume raw Ollama JSON directly.

---

## `InferenceRequest`

`InferenceRequest` provides normalized application fields such as:

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

The backend adapter translates these fields into its own native request protocol.

For example:

```text
Local AI Router:
thinking_enabled

Ollama:
think
```

Higher application layers should not need to know the backend-specific field name.

---

## `InferenceResult`

`InferenceResult` provides normalized result and telemetry fields such as:

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

A backend may expose different native names or omit some metrics.

Unavailable metrics remain unavailable rather than being guessed.

Backend-specific values that do not yet have a normalized field can be retained in:

```text
backend_metrics
```

---

## Immutability tests

Shared application data objects such as routing decisions and inference contracts are intentionally immutable where appropriate.

Tests verify that fields cannot be changed accidentally after creation.

This is particularly important for benchmarking because a request or measured result should not silently change after execution begins.

---

## Benchmark dataset testing

Benchmark dataset tests validate the version-controlled benchmark definition files.

Current validations include:

- valid JSON structure;
- unique case identifiers;
- required fields;
- supported categories and values;
- referenced fixture existence;
- routing expectations;
- scoring expectations.

These tests protect benchmark definitions before any model inference occurs.

---

## SQLAlchemy metadata testing

Database model tests validate schema structure without always requiring a live database.

They verify details such as:

- table registration;
- PostgreSQL schema assignment;
- primary keys;
- foreign keys;
- unique constraints;
- nullability;
- JSONB usage;
- deletion behavior.

These tests are fast and catch many database-design errors before migration generation.

---

## ORM relationship testing

SQLAlchemy can delay full relationship validation until an ORM query is executed.

For that reason, metadata tests alone are not sufficient.

The test suite explicitly calls:

```python
configure_mappers()
```

to verify that relationships and their corresponding `back_populates` names are valid.

This catches errors such as:

```text
benchmark_case_result
```

being accidentally defined on one side while another model expects:

```text
benchmark_case_results
```

without needing to wait for application runtime to expose the problem.

---

## PostgreSQL integration testing

Some benchmark persistence behavior requires a real PostgreSQL database.

Integration tests use:

```text
local_ai_router_test
```

rather than the normal development database.

These tests verify behavior such as:

- real foreign-key persistence;
- historical benchmark runs;
- quality-score storage;
- performance-metric storage;
- multi-run historical querying.

Tests refuse to execute database mutations against a database other than:

```text
local_ai_router_test
```

where appropriate.

---

## Transaction-isolated database tests

Synthetic benchmark runs created during PostgreSQL integration tests are wrapped in a database transaction.

At the end of the test, the transaction is rolled back.

This means tests can verify real PostgreSQL behavior without permanently storing synthetic benchmark history.

The pattern is:

```text
connect to test database
        ↓
begin transaction
        ↓
seed required configuration
        ↓
insert synthetic benchmark run/results
        ↓
query and assert behavior
        ↓
rollback transaction
```

This allows repeated execution while keeping the test database predictable.

---

## Idempotent test seeding

Stable synthetic benchmark configuration can be seeded into:

```text
local_ai_router_test
```

The seed process is idempotent.

Running it repeatedly reuses the existing rows instead of creating duplicate:

- models;
- quantizations;
- model variants;
- model profiles;
- benchmark definitions;
- benchmark cases;
- benchmark suites;
- hardware profiles;
- runtime profiles;
- context profiles.

The seeding command deliberately refuses to run against the primary development benchmark database.

---

## Historical benchmark testing

The benchmark persistence test suite verifies that repeated executions are append-oriented.

For example, two runs may use the same:

```text
model profile
benchmark suite
hardware profile
runtime profile
context profile
benchmark case
```

while producing different:

```text
benchmark_run_id
quality score
latency
VRAM usage
```

Both records must remain independently queryable.

This directly protects the architectural requirement that benchmark history must not be overwritten by later runs.

---

## Real inference testing

Tests requiring a real Ollama instance or local model should not be part of normal GitHub-hosted CI.

Those tests depend on resources specific to the local AI environment, including:

- Ollama;
- installed model files;
- GPU hardware;
- model-loading time;
- driver configuration;
- backend runtime state.

Real inference should therefore remain an explicitly invoked smoke-test or benchmark workflow.

Routine CI should validate application behavior using mocks and deterministic tests.

---

## Automated benchmark testing

Automated model benchmarks are conceptually different from ordinary unit tests.

A benchmark may:

- load a large model;
- consume significant VRAM;
- run for minutes;
- produce stochastic outputs;
- depend on current model artifacts;
- record persistent results.

These should not run every time a normal unit test executes.

Instead, the benchmark runner will become a separately invoked application workflow.

Normal tests will validate that the runner itself behaves correctly using fake or mocked inference executors.

Real benchmark execution will be explicitly requested.

---

## Failed-case testing

Benchmark execution must preserve useful diagnostics when individual cases fail.

The runner should distinguish between failures such as:

- inference backend unavailable;
- timeout;
- invalid model response;
- deterministic scoring failure;
- structured-output validation failure;
- unexpected application exception.

Tests should verify both:

- user-readable failure information;
- preserved technical diagnostics suitable for troubleshooting.

Raw Python tracebacks or SQL exceptions should not be treated as the user-facing error interface.

---

## Static type-checking strategy

Static type checking will be introduced incrementally rather than enabled as an artificial pass/fail gate before the project's typing conventions are stable.

The planned static type checker is **Pyright**.

Pyright is a good fit because:

- the project already uses Python type annotations extensively;
- it integrates well with VS Code;
- local and CI checks can share the same type model;
- it supports gradual adoption;
- strictness can increase as architecture stabilizes.

---

## Typing conventions

The project prefers explicit application-level types for important interfaces.

Examples include:

- routing modes;
- routing decisions;
- inference requests;
- inference results;
- API request and response schemas;
- model identifiers;
- benchmark records;
- database entities;
- future context contracts;
- future retrieval contracts;
- future tool contracts.

Descriptive field names should remain consistent across architectural layers.

Examples already established include:

```text
route_mode
thinking_enabled
route_reason
model_name
user_message
```

Backend-specific field names should remain isolated to backend adapters.

---

## Staged static-analysis adoption

### Stage 1 — current state

Use Python type annotations where interfaces are clear.

Do not make type checking a mandatory CI gate yet.

### Stage 2 — establish shared contracts

Continue replacing loosely structured dictionaries with typed application contracts.

Run Pyright locally and resolve significant issues.

### Stage 3 — baseline CI checking

Add Pyright to development dependencies and GitHub Actions.

Begin with a practical configuration that the existing codebase can satisfy consistently.

### Stage 4 — increase strictness

Increase type-checking strictness in important areas such as:

- routing;
- inference contracts;
- schemas;
- benchmark infrastructure;
- persistence;
- retrieval;
- model registry;
- tool interfaces.

Strictness should increase deliberately rather than creating a large backlog of low-value type errors.

---

## CI principle

A quality gate should only become mandatory when the project has a defined convention for satisfying it.

Ruff and pytest are enforced because their conventions are established.

Static typing will become an enforced gate after the application's shared type contracts and typing conventions are sufficiently mature.

This prevents CI from becoming noisy while preserving the long-term goal of strong static validation.

---

## Future CI evolution

As the project grows, CI may later include:

- Pyright static type checking;
- automated PostgreSQL service containers;
- migration validation;
- migration downgrade/upgrade tests;
- benchmark-runner orchestration tests;
- benchmark regression checks;
- API contract tests;
- security and dependency scanning;
- frontend tests;
- build validation;
- deployment packaging checks.

GPU-dependent model benchmarks and real inference validation should remain separate from ordinary fast CI unless dedicated self-hosted infrastructure is introduced.

---

## Testing principle

Each architectural layer should be tested at the narrowest boundary that can prove its responsibility.

Examples:

```text
routing tests
    prove routing behavior

inference-contract tests
    prove application data contracts

adapter tests
    prove backend translation

API tests
    prove HTTP behavior

metadata tests
    prove schema design

database integration tests
    prove PostgreSQL behavior

benchmark runner tests
    prove orchestration

real benchmarks
    measure actual models
```

This separation improves failure diagnosis and prevents unrelated subsystems from becoming unnecessarily coupled during testing.

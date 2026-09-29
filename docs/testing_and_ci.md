# Local AI Router — Testing and CI Strategy

## Overview

The Local AI Router uses deterministic automated tests and lightweight quality
checks to protect runtime routing behavior.

The normal router test suite must not require:

- PostgreSQL;
- Alembic migrations;
- the Local AI Benchmark repository;
- benchmark datasets;
- a GPU;
- a running Ollama instance.

This keeps development and GitHub-hosted CI fast and reproducible, including for
people who fork only the router repository.

## Current quality gates

### Dependency consistency

```bash
python -m pip check
```

### Ruff linting

```bash
ruff check src tests
```

### Ruff formatting

```bash
ruff format --check src tests
```

Apply formatting locally with:

```bash
ruff format src tests
```

### Automated tests

```bash
python -m pytest -v
```

The deterministic suite covers:

- routing policy behavior;
- routing contracts;
- API request/response behavior;
- normalized inference contracts;
- Ollama adapter translation;
- repository/service-boundary enforcement.

## GitHub Actions

The CI workflow is defined in:

```text
.github/workflows/ci.yml
```

For pushes and pull requests it installs the locked development environment,
installs the router package, checks dependency consistency, runs Ruff, and runs
pytest.

Normal CI does not require Ollama or GPU hardware.

## Routing tests

Routing tests protect deterministic routing behavior and stable routing
contracts.

Important fields include:

- `route_mode`;
- `route_reason`;
- `thinking_enabled`.

The current v1 policy is intentionally simple and serves as a baseline for
future Routing Intelligence.

## API tests

FastAPI tests validate schema behavior, route/chat responses, default model
selection, and readable backend failures.

Ollama communication is mocked so these tests do not depend on a local model.

## Inference-contract tests

`InferenceRequest` and `InferenceResult` provide backend-independent
contracts.

Tests verify stable fields, optional generation settings, telemetry
preservation, and immutability.

## Backend-adapter tests

Ollama adapter tests verify both directions:

```text
InferenceRequest
    ↓
Ollama request payload
```

and:

```text
Ollama response payload
    ↓
InferenceResult
```

Ollama-specific protocol details remain isolated inside the adapter.

## Service-boundary tests

Architecture tests protect the repository split.

Router source must not import implementation modules from:

```text
local_ai_benchmark
```

Documentation may discuss Local AI Benchmark as an optional external producer of
capability data. The prohibited relationship is a runtime implementation
dependency.

## Real inference testing

Real Ollama/model smoke tests remain separate from ordinary CI because they
depend on environment-specific resources such as installed models, GPU
hardware, drivers, and backend state.

## Benchmark ownership

Model benchmarking is not part of this repository's normal test suite.

The standalone `local-ai-benchmark` repository owns:

- benchmark datasets;
- benchmark execution;
- scoring;
- PostgreSQL persistence;
- historical comparisons;
- candidate-model evaluation;
- benchmark reporting.

Router tests may evaluate routing behavior, but they do not execute or persist
model benchmark suites.

## Optional future benchmark integration

Future Routing Intelligence may consume compact capability/evaluation data
published by the Benchmark Service.

That integration must remain optional.

```text
Benchmark Service unavailable
    ↓
benchmark-derived updates unavailable
    ↓
router continues operating
    ↓
configured/default/last-known routing information is used
```

A Benchmark Service failure must not make `/route` or `/chat` unavailable.

## Static type checking

Pyright remains the planned static type checker.

It should become a mandatory CI gate only after the repository has stable typing
conventions and a configuration the existing code can satisfy consistently.

## Testing principle

```text
routing tests
    prove routing behavior

inference-contract tests
    prove normalized data contracts

adapter tests
    prove backend translation

API tests
    prove HTTP behavior

service-boundary tests
    prove repository independence

real inference smoke tests
    prove environment-specific integration
```

Each layer is tested at the narrowest boundary that proves its responsibility.

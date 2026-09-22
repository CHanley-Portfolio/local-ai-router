# Local AI Router — Testing, CI, and Static Type-Checking Strategy

## Overview

The Local AI Router uses automated testing and code-quality checks to detect regressions as the project grows.

The development workflow is designed so the same core quality gates can be run both:

* locally before committing code;
* automatically through GitHub Actions after pushes and pull requests.

Normal CI execution does not require Ollama, a GPU, or a downloaded AI model.

This keeps the automated pipeline deterministic and suitable for standard GitHub-hosted runners.

## Current quality gates

The current CI pipeline performs the following checks.

### Dependency consistency

```bash
python -m pip check
```

This verifies that installed package dependencies are internally compatible.

### Ruff linting

```bash
ruff check src tests
```

Ruff currently checks:

* important Python syntax and style errors;
* undefined or invalid names;
* unused imports and related Pyflakes issues;
* import ordering.

The initial rule set is intentionally focused rather than enabling every available Ruff rule immediately.

Rules can be expanded as the project matures.

### Ruff formatting

```bash
ruff format --check src tests
```

CI checks formatting but does not modify source files.

Formatting changes should be applied locally with:

```bash
ruff format src tests
```

This ensures repository changes remain deliberate and reviewable.

### Automated tests

```bash
python -m pytest -v
```

The normal automated suite currently contains unit and API/integration tests that do not require a running Ollama service or GPU.

Real inference smoke testing remains separate from routine CI.

## GitHub Actions

The CI workflow is defined in:

```text
.github/workflows/ci.yml
```

It runs automatically for:

* repository pushes;
* pull requests.

The workflow creates a clean GitHub-hosted environment, installs Python 3.12, installs the locked development dependencies, installs the Local AI Router package, and executes the configured quality gates.

A CI failure therefore indicates that at least one required repository validation did not pass.

## Local development workflow

Before pushing significant changes, the primary local checks are:

```bash
ruff check src tests
ruff format --check src tests
python -m pytest -v
```

These intentionally match the important checks performed by GitHub Actions.

Developers can fix formatting locally with:

```bash
ruff format src tests
```

and automatically repair supported lint violations with:

```bash
ruff check --fix src tests
```

Automatic fixes should be reviewed before committing.

## Real inference testing

Tests requiring a real Ollama instance or local model should not be part of normal GitHub-hosted CI.

Those tests depend on resources that are specific to the local AI environment, including:

* Ollama;
* installed model files;
* GPU hardware;
* model-loading time;
* local runtime configuration.

Real inference should therefore remain an explicitly invoked smoke-test or benchmark workflow.

Routine CI should validate application behavior using mocks and deterministic tests.

## Static type-checking strategy

Static type checking will be introduced incrementally rather than enabled as an artificial pass/fail gate before the project's typing conventions are stable.

The planned static type checker is **Pyright**.

Pyright is a good fit for this project because:

* the project already uses Python type annotations extensively;
* it integrates well with VS Code;
* the same type-checking model can be used during editing and in CI;
* it supports gradual adoption;
* it can become stricter as the application architecture stabilizes.

## Typing conventions

The project will prefer explicit application-level types for important interfaces.

Examples include:

* routing modes;
* routing decisions;
* request and response schemas;
* model identifiers;
* backend interfaces;
* benchmark records;
* database entities;
* context and retrieval contracts;
* tool request and response contracts.

Descriptive field names should remain consistent across architectural layers.

Examples already established by the router include:

```text
route_mode
thinking_enabled
route_reason
model_name
user_message
```

Backend-specific field names should remain isolated to backend adapters when appropriate.

For example, the router may expose:

```text
thinking_enabled
```

while the Ollama API internally expects:

```text
think
```

## Centralized data contracts

As the router architecture expands, shared routing and application data contracts should be centralized rather than recreated independently across modules.

This will make static typing more valuable because route handlers, routing logic, model-selection systems, benchmarks, and persistence layers will share known structures.

Future typed objects may include:

* routing requests;
* routing decisions;
* capability requirements;
* model capability profiles;
* benchmark results;
* inference requests;
* inference results;
* context assembly metadata;
* retrieval results.

## Staged adoption

Static type checking will be introduced in stages.

### Stage 1 — current state

Use Python type annotations where interfaces are already clear.

Do not make type checking a mandatory CI gate yet.

### Stage 2 — establish shared contracts

As centralized routing/data objects are introduced, define explicit types for stable application boundaries.

Run Pyright locally and resolve significant issues.

### Stage 3 — baseline CI checking

Add Pyright to development dependencies and GitHub Actions.

Begin with a practical configuration that the existing codebase can satisfy consistently.

### Stage 4 — increase strictness

Increase type-checking strictness in important architectural areas such as:

* routing;
* schemas;
* model registry;
* database access;
* benchmark infrastructure;
* retrieval;
* tool interfaces.

Strictness should increase deliberately rather than generating a large backlog of low-value typing errors.

## CI principle

A quality gate should only be mandatory when the project has a defined convention for satisfying it.

For that reason, Ruff and pytest are enforced now because their conventions are established.

Static typing will become an enforced gate after the application's shared type contracts and typing conventions are sufficiently mature.

This prevents CI from becoming noisy while preserving the long-term goal of strong static validation.

## Future CI evolution

As the project grows, CI may later include:

* Pyright static type checking;
* database migration validation;
* benchmark regression checks;
* API contract tests;
* security/dependency scanning;
* frontend tests;
* build validation;
* deployment packaging checks.

GPU-dependent model benchmarks and real inference validation will remain separate from ordinary fast CI unless dedicated self-hosted infrastructure is introduced.

# Local AI Router — Project Structure

## Purpose

The Local AI Router is a standalone runtime routing service.

Its core responsibility is to accept a request, classify what the request needs,
select an appropriate route/model, and execute inference through a backend
adapter.

The router is intentionally independent from the standalone Local AI Benchmark
Service. A user can install, fork, run, and extend the router without installing
PostgreSQL, Alembic, benchmark datasets, or the benchmark repository.

Benchmark-derived capability information may become an optional input to future
Routing Intelligence, but it is not required for the router to operate.

## Current repository structure

```text
local-ai-router/
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/
│   ├── project_structure.md
│   ├── routing_policy_v1.md
│   └── testing_and_ci.md
├── src/
│   └── local_ai_router/
│       ├── __init__.py
│       ├── config.py
│       ├── main.py
│       ├── schemas.py
│       ├── inference/
│       │   ├── __init__.py
│       │   ├── ollama_client.py
│       │   └── data/
│       │       ├── __init__.py
│       │       ├── inference_request.py
│       │       └── inference_result.py
│       └── routing/
│           ├── __init__.py
│           ├── router.py
│           └── data/
│               ├── __init__.py
│               ├── routing_decision.py
│               └── routing_types.py
├── tests/
│   ├── test_chat_api.py
│   ├── test_inference_contracts.py
│   ├── test_ollama_client.py
│   ├── test_route_api.py
│   ├── test_routing.py
│   ├── test_routing_contracts.py
│   └── test_service_boundaries.py
├── .gitignore
├── pyproject.toml
├── requirements.lock.txt
└── requirements-dev.lock.txt
```

Inference contracts and backend adapters now live under
`local_ai_router/inference`. The router repository therefore exposes one
coherent runtime package and does not require a separate shared-inference
package.

## HTTP/API layer

`local_ai_router.main` owns FastAPI application orchestration.

Current endpoints include:

- `GET /health`
- `GET /models`
- `POST /route`
- `POST /chat`

The API layer coordinates application components rather than containing backend
protocol parsing or benchmark execution.

## Routing layer

`local_ai_router.routing` owns runtime routing decisions.

Important normalized concepts include:

- `route_mode`
- `route_reason`
- `thinking_enabled`
- `model_name`

The current deterministic policy remains a regression-safe baseline. Future
Routing Intelligence can become more sophisticated without changing the basic
API contract.

## Inference boundary

The router uses backend-independent `InferenceRequest` and `InferenceResult`
contracts around backend adapters.

The normalized flow is:

```text
routing decision
    ↓
InferenceRequest
    ↓
backend adapter
    ↓
inference backend
    ↓
InferenceResult
    ↓
API response
```

Ollama is the first backend implementation.

Backend-specific field names and response structures stay inside the adapter.

## Configuration

`local_ai_router.config` currently owns lightweight runtime configuration such
as:

- Ollama base URL;
- default model.

The router has no required Benchmark Service database configuration.

## Standalone-service boundary

The Local AI Router and Local AI Benchmark are independent repositories.

```text
Local AI Router
    runs independently

Local AI Benchmark
    runs independently

optional future integration:
Benchmark capability/evaluation output
    ↓
explicit external contract
    ↓
Routing Intelligence
```

The router must not import `local_ai_benchmark` implementation modules.

The router must continue operating when the Benchmark Service is absent,
offline, or broken.

Future benchmark-derived capability information is optional evidence rather than
required runtime infrastructure.

## Persistence boundary

The standalone router currently has no required PostgreSQL persistence layer.

Benchmark PostgreSQL models, migrations, seed data, and historical results are
owned by the separate `local-ai-benchmark` repository.

If the broader Local AI Platform later requires project, conversation, memory,
or application persistence, that responsibility should be introduced behind an
explicit platform/service boundary rather than coupling the runtime router to
Benchmark Service persistence.

## Dependencies

Runtime dependencies are intentionally small:

- FastAPI;
- HTTPX.

Development dependencies include:

- pytest;
- Ruff;
- pip-tools.

PostgreSQL, Psycopg, SQLAlchemy, and Alembic are not required by the standalone
router.

## Quality gates

```bash
ruff format src tests
ruff check src tests
ruff format --check src tests
python -m pytest -v
```

## Architecture principle

The router stays focused on low-latency runtime decisions.

Heavy model evaluation, persistent benchmark storage, historical comparison,
candidate-model research, regression analysis, and benchmark reporting belong
to the standalone Benchmark Service.

This allows either repository to be used independently while preserving a clean
path for optional integration later.

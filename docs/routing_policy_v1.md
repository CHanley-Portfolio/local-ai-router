# Local AI Router — Routing Policy v1

## Overview

Routing Policy v1 is the first deterministic routing policy used by the Local AI Router.

Its purpose is to decide whether a user request should use normal fast inference or reasoning-enabled inference before the request is sent to the model backend.

This version is intentionally simple, transparent, and deterministic. It establishes a stable routing baseline that can be tested and benchmarked before more advanced routing strategies are introduced.

The policy currently supports two actual inference routes:

* `fast`
* `reasoning`

The public API also accepts `auto`, which instructs the router to choose between those two routes.

---

## Routing terminology

The project uses the following standardized routing fields.

### `route_mode`

`route_mode` represents either the route requested by the API caller or the route selected by the router.

Requests may contain:

* `auto`
* `fast`
* `reasoning`

Routing decisions contain:

* `fast`
* `reasoning`

`auto` is therefore a request mode rather than an inference route.

---

### `thinking_enabled`

`thinking_enabled` is an internal Boolean derived from the routing decision.

Its current relationship to `route_mode` is:

| Route       | `thinking_enabled` |
| ----------- | ------------------ |
| `fast`      | `False`            |
| `reasoning` | `True`             |

Clients do not directly supply `thinking_enabled`.

This separation prevents the public router API from being coupled to a backend-specific implementation detail.

When Ollama is used as the inference backend, `thinking_enabled` is translated into Ollama's `think` parameter by the Ollama adapter.

---

### `route_reason`

Every routing decision includes a human-readable `route_reason`.

This makes routing behavior observable rather than treating the router as a black box.

Examples include:

```text
Fast mode explicitly requested.
```

```text
Reasoning mode explicitly requested.
```

and:

```text
Automatic routing detected a reasoning-heavy request.
```

Automatic reasoning decisions may also include the markers that contributed to the decision.

---

## Explicit routing

Explicit routing always takes priority over automatic classification.

### Fast mode

A request containing:

```json
{
  "user_message": "What does CUDA stand for?",
  "route_mode": "fast"
}
```

produces a routing decision equivalent to:

```text
route_mode = "fast"
thinking_enabled = False
route_reason = "Fast mode explicitly requested."
```

No automatic-routing heuristics are evaluated.

---

### Reasoning mode

A request containing:

```json
{
  "user_message": "What does CUDA stand for?",
  "route_mode": "reasoning"
}
```

produces:

```text
route_mode = "reasoning"
thinking_enabled = True
route_reason = "Reasoning mode explicitly requested."
```

The complexity of the prompt does not override an explicit routing request.

---

## Automatic routing

When the caller supplies:

```text
route_mode = "auto"
```

the router evaluates the content of `user_message`.

Routing Policy v1 uses a simple scoring system.

The message is first normalized to lowercase so routing markers are evaluated without regard to capitalization.

The router then searches the message for known reasoning indicators.

Current reasoning markers include:

```text
analyze
analyzing
analysis
architecture
compare
debug
design
diagnose
evaluate
reason through
root cause
step by step
trade-offs
tradeoffs
troubleshoot
```

Each reasoning marker contributes two points to the routing score.

The current reasoning threshold is two points.

Therefore, one strong reasoning marker is currently sufficient to select the reasoning route.

---

## Prompt-length signals

Routing Policy v1 also contains two weak prompt-length indicators.

A request receives:

* one point when it contains at least 150 whitespace-separated words;
* one point when it contains at least 800 characters.

These signals are intentionally weaker than semantic reasoning markers.

Prompt length alone is not considered reliable evidence that a task requires deeper reasoning. A long request may still involve a simple task, while a short request may require substantial reasoning.

The two weak length indicators can currently combine to reach the two-point reasoning threshold.

These rules are part of the v1 baseline and are expected to evolve as the router gains stronger semantic classification and benchmark-driven routing.

---

## Routing decision algorithm

The current routing sequence is:

```text
Incoming request
      │
      ▼
Inspect route_mode
      │
      ├── fast ─────────────► Fast route
      │                       thinking_enabled=False
      │
      ├── reasoning ────────► Reasoning route
      │                       thinking_enabled=True
      │
      └── auto
           │
           ▼
     Normalize user_message
           │
           ▼
     Evaluate reasoning markers
           │
           ▼
     Evaluate weak length signals
           │
           ▼
     Calculate routing score
           │
           ├── score >= 2 ──► Reasoning route
           │
           └── score < 2 ───► Fast route
```

The routing policy itself performs no model inference.

This keeps the v1 routing decision fast, deterministic, inexpensive, and easy to test.

---

## `/route` endpoint

The `/route` endpoint exposes routing-policy evaluation without performing model inference.

Example request:

```json
{
  "user_message": "Analyze the trade-offs between these architectures.",
  "route_mode": "auto"
}
```

A response contains:

```json
{
  "route_mode": "reasoning",
  "thinking_enabled": true,
  "route_reason": "Automatic routing detected a reasoning-heavy request. Matched markers: analyze, trade-offs."
}
```

The exact list of matched markers depends on the request.

This endpoint is useful for:

* debugging routing behavior;
* automated routing evaluations;
* benchmark testing;
* observing routing decisions without loading an AI model.

---

## `/chat` routing flow

The `/chat` endpoint combines routing with actual inference.

Its current processing sequence is:

```text
ChatRequest
     │
     ▼
Resolve model_name
     │
     ▼
choose_route()
     │
     ▼
RoutingDecision
     │
     ├── route_mode
     ├── thinking_enabled
     └── route_reason
     │
     ▼
OllamaClient.chat()
     │
     ▼
Ollama /api/chat
     │
     ▼
ChatResponse
```

The public API uses router-level terminology such as `route_mode`.

The Ollama adapter translates the routing decision into backend-specific parameters such as:

```text
think=True
```

or:

```text
think=False
```

This boundary is intentional. It allows the router API to remain stable if additional inference backends are introduced later.

---

## Model selection

`ChatRequest` optionally accepts `model_name`.

When no model is explicitly supplied, `/chat` uses `DEFAULT_MODEL` from the router configuration.

The current architecture therefore separates two decisions:

1. which model performs inference;
2. which inference mode that model uses.

Routing Policy v1 primarily addresses the second decision.

Future versions of the Local AI Router will expand routing to select among multiple models based on task characteristics and benchmark data.

---

## Response metadata

`ChatResponse` returns both the generated answer and information describing how the request was processed.

Current routing-related fields are:

```text
model_name
route_mode
thinking_enabled
route_reason
```

Performance information supplied by Ollama may also be returned:

```text
total_duration_ns
eval_count
eval_duration_ns
```

Preserving this metadata is important for future benchmarking and observability work.

---

## Testing

Routing Policy v1 is protected by automated tests at multiple architectural layers.

### Routing unit tests

Directly test `choose_route()` without FastAPI or Ollama.

These tests verify:

* explicit fast routing;
* explicit reasoning routing;
* automatic fast routing;
* automatic reasoning routing.

### `/route` API tests

Verify the HTTP routing contract.

These tests protect standardized field names including:

```text
user_message
route_mode
thinking_enabled
route_reason
```

They also verify request validation and rejection of obsolete request-field names.

### `/chat` integration tests

Exercise the complete FastAPI `/chat` path while mocking Ollama.

These tests verify:

* fast routes disable thinking;
* reasoning routes enable thinking;
* the configured default model is used when no model is specified;
* Ollama communication failures become HTTP `503 Service Unavailable` responses;
* routing metadata survives through the complete API path.

### End-to-end smoke test

A real `/chat` request has also been tested against the local Ollama installation and the configured local model.

The smoke test verified the complete chain:

```text
HTTP client
    ↓
FastAPI
    ↓
routing policy
    ↓
OllamaClient
    ↓
Ollama
    ↓
local model
    ↓
ChatResponse
```

At completion of Routing Policy v1, the automated regression suite contains 12 passing tests.

---

## Limitations of v1

Routing Policy v1 is deliberately a baseline rather than the final routing architecture.

Its current limitations include:

* keyword/phrase matching;
* coarse prompt-length heuristics;
* no semantic task classifier;
* no routing confidence score;
* no hardware-load awareness;
* no model-quality benchmark lookup;
* no task-specific model selection;
* no project-context signal;
* no historical routing-performance feedback.

These limitations are intentional and documented.

The v1 policy gives the project a deterministic reference implementation against which future routing systems can be benchmarked.

---

## Planned evolution

Future router versions are expected to replace or augment the current rule-based scoring system with richer routing signals.

Planned areas include:

* semantic task classification;
* routing confidence scores;
* coding, analysis, reasoning, summarization, and other task categories;
* benchmark-driven model selection;
* model capability profiles;
* latency and resource-cost awareness;
* available VRAM and system-load signals;
* project and conversation context;
* retrieval requirements;
* model availability;
* historical benchmark performance;
* configurable routing policies.

The existing `RoutingDecision` abstraction and standardized API naming are intended to allow these capabilities to evolve without forcing client applications to depend on backend-specific implementation details.

---

## Design principle

Routing Policy v1 establishes an important architectural rule for the Local AI Router:

> Applications request capabilities from the router; they should not need to understand the implementation details of the inference backend.

For example, applications request:

```text
route_mode="fast"
```

or:

```text
route_mode="reasoning"
```

They do not need to know that the current Ollama backend implements this distinction using its `think` Boolean.

Maintaining this abstraction will allow the router to add models, inference engines, benchmarking systems, retrieval, memory, and more sophisticated routing strategies while preserving a stable interface for applications built on top of it.

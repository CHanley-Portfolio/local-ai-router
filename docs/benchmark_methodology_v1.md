# Local AI Router Benchmark Methodology v1

## 1. Purpose

The Local AI Router benchmark framework exists to measure whether a model, model configuration, routing strategy, runtime change, or context strategy improves the system for real project workloads.

The benchmark system must support repeatable comparison over time.

It should answer questions such as:

- Which model is strongest for coding?
- Which model is strongest for reasoning and analysis?
- Which model follows structured-output instructions most reliably?
- How much quality is lost when using a faster or smaller model?
- At what context size does retrieval or reasoning quality begin to degrade?
- How much VRAM does a model require under realistic workloads?
- Did a software, configuration, model, or routing change cause a regression?

Benchmark results must therefore preserve both answer quality and runtime-performance information.

A single overall benchmark score must not replace category-level results because different models may specialize in different capabilities.

The benchmark system is intended to become an evidence source for future routing decisions rather than a one-time model comparison tool.

---

## 2. Core benchmarking principle

Quality and performance are separate measurement dimensions.

A model that answers correctly but slowly and a model that answers incorrectly but quickly must not receive equivalent evaluations.

Each benchmark run should therefore produce two major groups of measurements.

### Quality measurements

Quality measurements evaluate what the model produced.

Examples include:

- correctness;
- reasoning quality;
- instruction compliance;
- code correctness;
- retrieval accuracy;
- structured-output validity;
- summarization fidelity.

### Performance measurements

Performance measurements evaluate the computational cost of producing the answer.

Examples include:

- total request latency;
- time to first token when available;
- prompt-processing time;
- output-generation time;
- output tokens per second;
- prompt tokens per second;
- model load time;
- VRAM usage;
- RAM usage.

Quality and performance may later be compared together when making routing decisions, but their raw measurements must remain separate.

---

## 3. Benchmark categories

Version 1 of the benchmark suite uses the following capability taxonomy.

| Category | Purpose | Typical scoring method |
| --- | --- | --- |
| General question answering | Measure factual and practical question-answering ability | Exact criteria or rubric |
| Reasoning / analysis | Measure multi-step reasoning, diagnosis, comparison, and trade-off analysis | Rubric |
| Coding | Measure code generation, debugging, modification, and explanation | Automated tests + rubric |
| Instruction following | Measure whether explicit constraints are followed correctly | Deterministic criteria |
| Summarization | Measure preservation of important information while reducing unnecessary content | Rubric / reference criteria |
| Structured output | Measure reliable production of JSON or other machine-readable structures | Parser / schema validation |
| Long-context retrieval | Measure ability to locate and use relevant information inside increasingly large contexts | Exact retrieval criteria |
| Project-context use | Measure whether supplied project documentation is used correctly and unrelated information is ignored | Project-specific criteria |
| Tool selection | Measure whether the system chooses the correct tool or action when tools are available | Classification accuracy |

Tool-selection benchmarks may remain inactive until the tools framework exists.

Performance measurements apply across all applicable categories rather than forming a competing quality category.

---

## 4. Benchmark case design

Every benchmark case must be independently identifiable and reproducible.

Each case should contain or reference at least:

| Field | Purpose |
| --- | --- |
| `case_id` | Stable unique identifier |
| `case_version` | Version of the benchmark case |
| `category` | Primary benchmark category |
| `tags` | Additional capabilities or workload descriptors |
| `prompt` | Exact input given to the model |
| `context` | Optional additional supplied context |
| `expected_criteria` | Conditions defining a successful answer |
| `scoring_method` | Method used to evaluate the output |
| `critical` | Whether failure represents a critical regression |
| `notes` | Human-readable explanation of the case |

Prompts must remain unchanged when results are being compared historically.

If a prompt materially changes, its benchmark-case version must change.

This prevents results from different tests from appearing directly comparable when the test itself has changed.

---

## 5. Scoring methods

Benchmark cases should use the most objective scoring mechanism appropriate for the task.

Preferred scoring methods are described below.

### Exact or deterministic scoring

Use when there is a clearly correct answer.

Examples:

- known factual answers;
- extracted identifiers;
- classification results;
- required values;
- exact route selection.

### Schema validation

Use for structured output.

Examples:

- valid JSON;
- required properties;
- correct field types;
- prohibited extra fields.

### Automated execution

Use for code where practical.

Examples:

- unit tests;
- expected function output;
- exception behavior;
- API contract tests.

Passing executable tests should carry more weight than subjective review of whether generated code appears reasonable.

### Retrieval scoring

Use where information must be identified from provided context.

Potential measures include:

- exact answer accuracy;
- retrieval precision;
- retrieval recall;
- source identification accuracy.

### Rubric scoring

Use when an answer cannot reasonably be reduced to one exact value.

Rubric-scored cases should use several explicit criteria rather than a single subjective impression.

Each criterion uses a 0–4 scale:

| Score | Meaning |
| ---: | --- |
| 0 | Missing, incorrect, or unusable |
| 1 | Major errors or substantial omissions |
| 2 | Partially correct but important weaknesses remain |
| 3 | Correct and useful with only minor deficiencies |
| 4 | Fully satisfies the criterion |

Rubric scores are normalized to a 0–100 quality score for storage and comparison.

For example, four criteria with scores:

```text
4
3
4
3
```

produce:

```text
14 / 16 = 87.5
```

The stored normalized quality score would therefore be:

```text
87.5
```

The original criterion-level scores must also be preserved rather than storing only the normalized result.

---

## 6. Category scoring

Results should be reported per benchmark category.

For example:

```text
General QA             92.0
Reasoning              84.5
Coding                 94.0
Instruction following  97.0
Structured output      100.0
```

A macro average may later be calculated for convenience, but it must not hide category-level results.

This is particularly important for multi-model routing because the objective is not necessarily to identify one universal model.

The benchmark framework should be capable of identifying different models for different roles.

---

## 7. Benchmark reproducibility

Every benchmark run must record enough information to reproduce the environment as closely as practical.

The exact prompt, context, expected scoring criteria, model configuration, runtime configuration, and hardware state must be retained.

Raw model responses must also be preserved.

A final score without the underlying response is insufficient because scoring methodologies may improve later.

Preserving raw responses allows historical benchmark runs to be re-evaluated without necessarily rerunning model inference.

Historical results should be append-oriented.

Repeating a benchmark must create a new benchmark run rather than overwriting the previous one.

---

## 8. Model metadata

Each benchmark run must identify the model precisely.

Model metadata should include:

| Field | Example |
| --- | --- |
| Logical model name | `qwen3.5-9b-32k` |
| Model family | Qwen |
| Parameter size | 9B |
| Quantization | Model-specific value |
| Model digest/hash | Backend-provided identifier |
| Model source | Ollama / Hugging Face / other |
| Model version | When available |
| License/source reference | When applicable |

The display name alone is not sufficient because model files or quantizations may change while retaining similar names.

Model identity is therefore separated from specific loadable variants and inference profiles.

---

## 9. Inference configuration metadata

Inference settings can materially affect both answer quality and performance and must be preserved.

Record applicable settings such as:

- context-window configuration;
- actual prompt/context token count;
- maximum generated tokens;
- temperature;
- top-p;
- seed where supported;
- reasoning/thinking configuration;
- runtime-specific model parameters.

Initial benchmark runs should prefer deterministic or low-variance inference settings where appropriate.

If stochastic generation is intentionally tested, multiple trials should be recorded rather than assuming one generation represents typical behavior.

---

## 10. Normalized inference contracts

Benchmark execution should use the Local AI Router's normalized inference contracts rather than communicating directly with a specific inference backend.

The benchmark runner constructs an:

```text
InferenceRequest
```

describing the requested model execution.

The inference adapter translates that request into the native backend protocol.

The backend response is then converted into:

```text
InferenceResult
```

before it is returned to benchmark infrastructure.

The execution boundary is:

```text
BenchmarkRunner
      ↓
InferenceRequest
      ↓
backend adapter
      ↓
inference backend
      ↓
backend adapter
      ↓
InferenceResult
      ↓
scoring / persistence
```

The benchmark runner therefore does not need to understand Ollama-specific JSON structures.

---

## 11. `InferenceRequest`

`InferenceRequest` currently supports normalized fields including:

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

These names represent Local AI Router concepts.

A backend adapter is responsible for converting them into the appropriate native fields.

For example:

```text
Local AI Router:
thinking_enabled

Ollama:
think
```

This keeps benchmark orchestration independent from the current inference engine.

---

## 12. `InferenceResult`

`InferenceResult` provides normalized response and performance information.

Current fields include:

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

This normalized object becomes the input to benchmark scoring and persistence.

As a result, adding another inference backend should require a new adapter rather than changes throughout:

- the benchmark runner;
- scoring logic;
- API code;
- PostgreSQL persistence;
- comparison systems.

---

## 13. Backend-specific telemetry

Not every backend exposes the same measurements.

Backend-native telemetry should be normalized into `InferenceResult` fields where equivalent concepts exist.

For example, Ollama currently exposes values such as:

```text
total_duration
load_duration
prompt_eval_count
prompt_eval_duration
eval_count
eval_duration
```

These become normalized values such as:

```text
total_duration_ns
model_load_duration_ns
prompt_token_count
prompt_eval_duration_ns
output_token_count
output_eval_duration_ns
```

Backend-specific measurements that do not yet have a standardized field may be retained in:

```text
backend_metrics
```

rather than discarded.

This preserves useful telemetry while keeping the benchmark runner independent from one backend.

Unavailable measurements must remain unavailable rather than being estimated without evidence.

---

## 14. Hardware metadata

Hardware state must be attached to performance measurements.

At minimum record:

| Component | Required metadata |
| --- | --- |
| GPU | Model |
| VRAM | Total capacity |
| NVIDIA driver | Driver version |
| CUDA | Runtime/API version where available |
| CPU | Processor model |
| System RAM | Installed memory |
| Operating system | Distribution/version |
| Kernel | Kernel version where relevant |

For the current development workstation, the benchmark system should recognize the RTX 5060 Ti 16 GB environment as the baseline hardware profile.

Changing significant hardware must create a distinct hardware profile rather than silently mixing results.

---

## 15. Runtime metadata

Software configuration must also be retained.

Relevant values include:

- Local AI Router version or Git commit;
- Ollama version;
- inference backend;
- Python version where router code participates;
- benchmark-suite version;
- benchmark-case version;
- operating-system environment;
- relevant backend configuration.

The Git commit identifier is particularly useful because it connects benchmark results directly to the code that produced them.

---

## 16. Context metadata

Context behavior can materially affect both model quality and performance.

Context configuration should be recorded separately from model configuration.

Relevant values may include:

- configured context-window size;
- context strategy;
- whether retrieval is enabled;
- retrieval top-k;
- chunk size;
- chunk overlap;
- backend-specific context options.

The same model profile may therefore be evaluated under different context strategies without treating those configurations as different model identities.

---

## 17. Performance metrics

Where supported, record:

| Metric | Purpose |
| --- | --- |
| Model load duration | Cost of loading the model |
| Prompt token count | Size of model input |
| Prompt evaluation duration | Time spent processing input |
| Prompt tokens/sec | Prompt-processing throughput |
| Output token count | Generated output size |
| Output generation duration | Time spent producing tokens |
| Output tokens/sec | Generation throughput |
| Total duration | End-to-end inference duration |
| Time to first token | User-perceived initial response latency |
| Peak VRAM | Maximum GPU-memory usage |
| Baseline VRAM | GPU-memory state before inference |
| Peak RAM | System-memory cost where practical |

Not every backend will expose every measurement.

Unavailable values should be stored as unavailable rather than replaced with estimated values.

Derived metrics such as tokens per second may be calculated from raw counts and durations where appropriate, while preserving the original raw measurements.

---

## 18. Quality and performance separation

Quality scores and runtime measurements must remain structurally separate.

A benchmark case result may therefore have:

```text
BenchmarkCaseResult
    ├── BenchmarkQualityScore
    └── BenchmarkPerformanceMetric
```

This makes it possible to ask questions such as:

- Which model produces the highest coding quality?
- Which model produces acceptable coding quality with lower latency?
- Which quantization saves VRAM without causing unacceptable quality loss?
- Which model is strongest for reasoning even if it is not the fastest?

An overall ranking should not destroy the underlying quality and performance measurements.

---

## 19. Warm and cold benchmark runs

Model loading can distort latency results.

Performance testing should distinguish between different execution conditions.

### Cold run

The model is not already resident and model-loading cost is included.

This measures startup behavior.

### Warm run

The model is already loaded and ready for inference.

This better represents repeated interactive use.

Cold and warm results must not be averaged together without retaining their run type.

---

## 20. Raw benchmark data

Every benchmark execution should preserve enough information to explain the result later.

Raw records should include:

```text
benchmark case
exact prompt
supplied context
raw model response
scoring result
criterion-level scores
timing information
token counts
model configuration
runtime information
hardware profile
context profile
errors or warnings
timestamp
router Git commit
```

PostgreSQL is the authoritative durable benchmark store.

Machine-readable summaries may also be emitted by the benchmark runner for reporting or automation, but standalone JSON result files should not replace the relational historical database.

---

## 21. Failed benchmark cases

A failed case is still useful benchmark evidence.

Failures should therefore be persisted rather than silently dropped.

Diagnostic records should distinguish conditions such as:

- inference backend unavailable;
- request timeout;
- malformed backend response;
- deterministic answer failure;
- structured-output validation failure;
- scorer error;
- unexpected execution exception.

A failed case should retain:

```text
result status
error type
readable error message
available raw response
diagnostic information
available timing data
```

The benchmark run should continue where possible rather than losing all previous results because one case fails.

Transactional boundaries must be designed carefully so persistence remains consistent.

---

## 22. Benchmark run identity

Every benchmark execution receives a unique durable run identifier.

A run connects:

```text
benchmark suite
model profile
hardware profile
runtime profile
context profile
router Git commit
run mode
run status
timestamps
```

Repeating the same suite with the same model and configuration must still create a separate run.

This preserves chronological history and allows regressions or improvements to be detected.

---

## 23. Historical comparisons

Historical runs should remain queryable independently.

For example:

```text
Run A
quality: 80
duration: 5 seconds
peak VRAM: 8.0 GB

Run B
quality: 95
duration: 4 seconds
peak VRAM: 7.5 GB
```

Both runs may use the same:

```text
benchmark suite
model profile
hardware profile
runtime profile
context profile
```

but must remain separate records.

Historical comparison is a core requirement rather than an optional reporting feature.

---

## 24. Regression thresholds v1

Initial regression thresholds are intentionally conservative and may be recalibrated after enough historical data exists.

### Critical benchmark cases

A previously passing critical deterministic case becoming a failure is considered a regression.

Examples may include:

- invalid required JSON output;
- broken API-contract generation;
- failure to retrieve explicitly supplied critical information;
- failure of required generated-code tests.

### Quality-score regression

For category-level normalized scores:

```text
0–2 point decrease:
    normal measurement variation

>2 and <5 point decrease:
    warning / investigate

>=5 point decrease:
    regression
```

A quality regression should take priority over a performance improvement unless the change was explicitly intended and documented.

### Latency regression

When comparing the same model, benchmark suite, configuration, and hardware:

```text
<10% slower:
    normal variation

10–20% slower:
    warning / investigate

>20% slower:
    performance regression
```

### Throughput regression

For output tokens per second:

```text
<10% decrease:
    normal variation

10–20% decrease:
    warning / investigate

>20% decrease:
    performance regression
```

### VRAM regression

When model, configuration, and context are otherwise equivalent:

```text
<5% increase:
    normal variation

5–10% increase:
    warning / investigate

>10% increase:
    memory regression
```

These thresholds are version-1 engineering guardrails rather than universal industry standards.

They should be recalibrated from observed variance once repeated benchmark data is available.

---

## 25. Benchmark comparison rules

Two benchmark results should only be treated as directly comparable when important experimental conditions are compatible.

Comparisons should consider:

- benchmark-suite version;
- benchmark-case version;
- hardware profile;
- model version;
- quantization;
- inference configuration;
- context configuration;
- routing/reasoning configuration;
- backend/runtime version;
- cold versus warm execution.

The application may still display results from different configurations, but it must identify those differences rather than presenting them as controlled comparisons.

---

## 26. External reference results

Externally published benchmark results are useful for context but must remain separate from locally measured runs.

Examples may include scores published by:

- model developers;
- benchmark maintainers;
- research papers;
- trusted evaluation projects.

Reference results should retain provenance such as:

```text
benchmark definition
model variant
source name
source URL
metric name
score
evaluation split
context length
reported date
source-specific metadata
```

An external score must never be represented as though it were produced by the Local AI Router's own hardware and benchmark runner.

---

## 27. External and project-specific benchmarks

The Local AI Router uses two complementary benchmark sources.

### Standard external benchmarks

Established benchmark suites may be used where they provide useful standardized measures.

These provide broader comparisons against common language-model tasks.

### Local project benchmarks

Custom benchmark cases represent the workloads the Local AI Router is actually intended to perform.

Examples include:

- Python/FastAPI work;
- software architecture;
- debugging;
- PostgreSQL design;
- project-document retrieval;
- structured routing output;
- long-context document use;
- project-specific context handling.

External benchmark performance must not substitute for testing actual project workloads.

---

## 28. Test dataset versus benchmark results

Version-controlled JSON benchmark datasets define test cases.

They are not the authoritative long-term result store.

The separation is:

```text
JSON / fixtures
    define benchmark cases

PostgreSQL
    stores benchmark execution history
```

This prevents benchmark results from becoming scattered across ad hoc terminal output or many result JSON files.

---

## 29. Benchmark database integrity

The benchmark persistence layer uses explicit relational entities for reproducibility.

Major relationships include:

```text
Model
    ↓
ModelVariant
    ↓
ModelProfile
    ↓
BenchmarkRun
    ↓
BenchmarkCaseResult
    ├── BenchmarkQualityScore
    └── BenchmarkPerformanceMetric
```

Benchmark definitions and suites connect separately to the executed run:

```text
BenchmarkDefinition
    ↓
BenchmarkCase
    ↓
BenchmarkSuite
    ↓
BenchmarkRun
```

Hardware, runtime, and context configuration also attach to the run.

This creates a durable record of what was tested, where it ran, how it was configured, what it produced, how it scored, and what resources it consumed.

---

## 30. Benchmark evolution

Benchmark suites and scoring methods will evolve as the Local AI Router gains capabilities.

Future suites may evaluate:

- vision;
- tool calling;
- retrieval-augmented generation;
- memory;
- routing decisions;
- model selection;
- reasoning-effort selection;
- agent workflows;
- multimodal context.

Historical suite versions must remain identifiable so old results retain meaning.

If a test changes materially, the case or suite version should change instead of rewriting the historical definition.

---

## 31. Future model-selection use

Benchmark data is intended eventually to inform model routing.

For example, historical evidence may show:

```text
Model A
strongest coding quality

Model B
strong reasoning quality with lower latency

Model C
best structured-output reliability

Model D
best performance under limited VRAM
```

The router may later use these capability profiles when selecting a model.

That logic should be evidence-driven rather than based on assumptions about model branding or parameter count.

---

## 32. Machine-readable summaries

The automated benchmark runner should eventually produce a machine-readable summary for each completed run.

A summary may include:

```text
benchmark_run_id
suite
model
run status
cases attempted
cases passed
cases failed
category scores
total duration
average throughput
peak VRAM
errors
```

The summary is useful for:

- CLI reporting;
- frontend dashboards;
- automation;
- regression reports;
- scheduled benchmark reviews.

The summary must reference the durable PostgreSQL run rather than becoming an independent authoritative store.

---

## 33. Design principle

The benchmark system exists to provide evidence for architectural decisions.

Models, routing policies, context limits, quantizations, inference backends, and runtime optimizations should not be promoted because they appear promising from one demonstration.

Changes should be evaluated using:

- reproducible workloads;
- preserved outputs;
- controlled configurations;
- normalized inference contracts;
- durable PostgreSQL history;
- quality scoring;
- performance telemetry;
- historical comparison.

The long-term goal is not simply to identify the highest-scoring model.

The goal is to build a router that can understand which model and configuration are most appropriate for a particular workload based on repeatable evidence.
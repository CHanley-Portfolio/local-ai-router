# Local AI Router Benchmark Methodology v1

## 1. Purpose

The Local AI Router benchmark framework exists to measure whether a model, model configuration, routing strategy, or runtime change improves the system for real project workloads.

The benchmark system must support repeatable comparison over time.

It should answer questions such as:

* Which model is strongest for coding?
* Which model is strongest for reasoning and analysis?
* Which model follows structured-output instructions most reliably?
* How much quality is lost when using a faster or smaller model?
* At what context size does retrieval or reasoning quality begin to degrade?
* How much VRAM does a model require under realistic workloads?
* Did a software, configuration, model, or routing change cause a regression?

Benchmark results must therefore preserve both answer quality and runtime-performance information.

A single overall benchmark score must not replace category-level results because different models may specialize in different capabilities.

---

## 2. Core benchmarking principle

Quality and performance are separate measurement dimensions.

A model that answers correctly but slowly and a model that answers incorrectly but quickly must not receive equivalent evaluations.

Each benchmark run should therefore produce two major groups of measurements:

### Quality measurements

Quality measurements evaluate what the model produced.

Examples include:

* correctness;
* reasoning quality;
* instruction compliance;
* code correctness;
* retrieval accuracy;
* structured-output validity;
* summarization fidelity.

### Performance measurements

Performance measurements evaluate the computational cost of producing the answer.

Examples include:

* total request latency;
* time to first token when available;
* prompt-processing time;
* output-generation time;
* output tokens per second;
* prompt tokens per second;
* model load time;
* VRAM usage;
* RAM usage.

Quality and performance may later be compared together when making routing decisions, but their raw measurements must remain separate.

---

## 3. Benchmark categories

Version 1 of the benchmark suite will use the following capability taxonomy.

| Category                   | Purpose                                                                                               | Typical scoring method      |
| -------------------------- | ----------------------------------------------------------------------------------------------------- | --------------------------- |
| General question answering | Measure factual and practical question-answering ability                                              | Exact criteria or rubric    |
| Reasoning / analysis       | Measure multi-step reasoning, diagnosis, comparison, and trade-off analysis                           | Rubric                      |
| Coding                     | Measure code generation, debugging, modification, and explanation                                     | Automated tests + rubric    |
| Instruction following      | Measure whether explicit constraints are followed correctly                                           | Deterministic criteria      |
| Summarization              | Measure preservation of important information while reducing unnecessary content                      | Rubric / reference criteria |
| Structured output          | Measure reliable production of JSON or other machine-readable structures                              | Parser / schema validation  |
| Long-context retrieval     | Measure ability to locate and use relevant information inside increasingly large contexts             | Exact retrieval criteria    |
| Project-context use        | Measure whether supplied project documentation is used correctly and unrelated information is ignored | Project-specific criteria   |
| Tool selection             | Measure whether the system chooses the correct tool or action when tools are available                | Classification accuracy     |

Tool-selection benchmarks may remain inactive until the tools framework exists.

Performance measurements apply across all applicable categories rather than forming a competing quality category.

---

## 4. Benchmark case design

Every benchmark case must be independently identifiable and reproducible.

Each case should eventually contain at least:

| Field               | Purpose                                          |
| ------------------- | ------------------------------------------------ |
| `case_id`           | Stable unique identifier                         |
| `case_version`      | Version of the benchmark case                    |
| `category`          | Primary benchmark category                       |
| `tags`              | Additional capabilities or workload descriptors  |
| `prompt`            | Exact input given to the model                   |
| `context`           | Optional additional supplied context             |
| `expected_criteria` | Conditions defining a successful answer          |
| `scoring_method`    | Method used to evaluate the output               |
| `critical`          | Whether failure represents a critical regression |
| `notes`             | Human-readable explanation of the case           |

Prompts must remain unchanged when results are being compared historically.

If a prompt materially changes, its benchmark-case version must change.

This prevents results from different tests from appearing directly comparable when the test itself has changed.

---

## 5. Scoring methods

Benchmark cases should use the most objective scoring mechanism appropriate for the task.

Preferred scoring methods are:

### Exact or deterministic scoring

Use when there is a clearly correct answer.

Examples:

* known factual answers;
* extracted identifiers;
* classification results;
* required values.

### Schema validation

Use for structured output.

Examples:

* valid JSON;
* required properties;
* correct field types;
* prohibited extra fields.

### Automated execution

Use for code where practical.

Examples:

* unit tests;
* expected function output;
* exception behavior;
* API contract tests.

Passing executable tests should carry more weight than subjective review of whether generated code appears reasonable.

### Retrieval scoring

Use where information must be identified from provided context.

Potential measures include:

* exact answer accuracy;
* retrieval precision;
* retrieval recall;
* source identification accuracy.

### Rubric scoring

Use when an answer cannot reasonably be reduced to one exact value.

Rubric-scored cases should use several explicit criteria rather than a single subjective impression.

Each criterion uses a 0–4 scale:

| Score | Meaning                                           |
| ----: | ------------------------------------------------- |
|     0 | Missing, incorrect, or unusable                   |
|     1 | Major errors or substantial omissions             |
|     2 | Partially correct but important weaknesses remain |
|     3 | Correct and useful with only minor deficiencies   |
|     4 | Fully satisfies the criterion                     |

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

---

## 8. Model metadata

Each benchmark run must identify the model precisely.

Model metadata should eventually include:

| Field                    | Example                       |
| ------------------------ | ----------------------------- |
| Logical model name       | `qwen3.5-9b-32k`              |
| Model family             | Qwen                          |
| Parameter size           | 9B                            |
| Quantization             | Model-specific value          |
| Model digest/hash        | Backend-provided identifier   |
| Model source             | Ollama / Hugging Face / other |
| Model version            | When available                |
| License/source reference | When applicable               |

The display name alone is not sufficient because model files or quantizations may change while retaining similar names.

---

## 9. Inference configuration metadata

Inference settings can materially affect both answer quality and performance and must be preserved.

Record applicable settings such as:

* context-window configuration;
* actual prompt/context token count;
* maximum generated tokens;
* temperature;
* seed where supported;
* reasoning/thinking configuration;
* batch configuration;
* runtime-specific model parameters.

Initial benchmark runs should prefer deterministic or low-variance inference settings where appropriate.

If stochastic generation is intentionally tested, multiple trials should be recorded rather than assuming one generation represents typical behavior.

---

## 10. Hardware metadata

Hardware state must be attached to performance measurements.

At minimum record:

| Component        | Required metadata                   |
| ---------------- | ----------------------------------- |
| GPU              | Model                               |
| VRAM             | Total capacity                      |
| NVIDIA driver    | Driver version                      |
| CUDA             | Runtime/API version where available |
| CPU              | Processor model                     |
| System RAM       | Installed memory                    |
| Operating system | Distribution/version                |
| Kernel           | Kernel version where relevant       |

For the current development workstation, the benchmark system should recognize the RTX 5060 Ti 16 GB environment as the baseline hardware profile.

Changing significant hardware must create a distinct hardware profile rather than silently mixing results.

---

## 11. Runtime metadata

Software configuration must also be retained.

Relevant values include:

* Local AI Router version or Git commit;
* Ollama version;
* inference backend;
* Python version where router code participates;
* benchmark-suite version;
* benchmark-case version;
* operating-system environment;
* relevant backend configuration.

The Git commit identifier is particularly useful because it connects benchmark results directly to the code that produced them.

---

## 12. Performance metrics

Where supported, record:

| Metric                     | Purpose                                 |
| -------------------------- | --------------------------------------- |
| Model load duration        | Cost of loading the model               |
| Prompt token count         | Size of model input                     |
| Prompt evaluation duration | Time spent processing input             |
| Prompt tokens/sec          | Prompt-processing throughput            |
| Output token count         | Generated output size                   |
| Output generation duration | Time spent producing tokens             |
| Output tokens/sec          | Generation throughput                   |
| Total duration             | End-to-end inference duration           |
| Time to first token        | User-perceived initial response latency |
| Peak VRAM                  | Maximum GPU-memory usage                |
| Baseline VRAM              | GPU-memory state before inference       |
| Peak RAM                   | System-memory cost where practical      |

Not every backend will expose every measurement.

Unavailable values should be stored as unavailable rather than replaced with estimated values.

---

## 13. Warm and cold benchmark runs

Model loading can distort latency results.

Performance testing should distinguish between:

### Cold run

The model is not already resident and model-loading cost is included.

This measures startup behavior.

### Warm run

The model is already loaded and ready for inference.

This better represents repeated interactive use.

Cold and warm results must not be averaged together without retaining their run type.

---

## 14. Raw benchmark data

Every benchmark execution should preserve raw run information.

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
errors or warnings
timestamp
```

PostgreSQL will become the durable benchmark store in a later issue.

The benchmark runner may also emit machine-readable intermediate results, but JSON files should not become the authoritative long-term historical database.

---

## 15. Regression thresholds v1

Initial regression thresholds are intentionally conservative and may be recalibrated after enough historical data exists.

### Critical benchmark cases

A previously passing critical deterministic case becoming a failure is considered a regression.

Examples may eventually include:

* invalid required JSON output;
* broken API-contract generation;
* failure to retrieve explicitly supplied critical information;
* failure of required generated-code tests.

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

When model/configuration/context are otherwise equivalent:

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

## 16. Benchmark comparison rules

Two benchmark results should only be treated as directly comparable when important experimental conditions are compatible.

Comparisons should consider:

* benchmark-suite version;
* benchmark-case version;
* hardware profile;
* model version;
* quantization;
* inference configuration;
* context configuration;
* routing/reasoning configuration;
* cold versus warm execution.

The application may still display results from different configurations, but it must identify those differences rather than presenting them as controlled comparisons.

---

## 17. External and project-specific benchmarks

The Local AI Router will use two complementary benchmark sources.

### Standard external benchmarks

Established benchmark suites may be used where they provide useful standardized measures.

These provide broader comparisons against common language-model tasks.

### Local project benchmarks

Custom benchmark cases will represent the workloads the Local AI Router is actually intended to perform.

Examples will include:

* Python/FastAPI work;
* software architecture;
* debugging;
* PostgreSQL design;
* project-document retrieval;
* structured routing output;
* long-context document use;
* project-specific context handling.

External benchmark performance must not substitute for testing actual project workloads.

---

## 18. Benchmark evolution

Benchmark suites and scoring methods will evolve as the Local AI Router gains capabilities.

Future suites may evaluate:

* vision;
* tool calling;
* retrieval-augmented generation;
* memory;
* routing decisions;
* model selection;
* reasoning-effort selection;
* agent workflows.

Historical suite versions must remain identifiable so old results retain meaning.

---

## 19. Design principle

The benchmark system exists to provide evidence for architectural decisions.

Models, routing policies, context limits, quantizations, and runtime optimizations should not be promoted because they appear promising from one demonstration.

Changes should be evaluated using reproducible workloads, preserved outputs, controlled configurations, and historical comparison.

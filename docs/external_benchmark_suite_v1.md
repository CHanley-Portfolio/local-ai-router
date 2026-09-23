# Local AI Router — External Benchmark Suite v1

## 1. Purpose

The Local AI Router uses established external benchmarks alongside custom project-specific evaluations.

External benchmarks provide two benefits:

1. They provide known datasets, evaluation rules, and expected answers that allow objective measurement.
2. They allow locally measured model performance to be compared with published or community benchmark results when experimental configurations are sufficiently compatible.

External benchmark scores do not replace Local AI Router workload testing.

A model may perform well on standardized academic benchmarks while performing poorly on the software-development, retrieval, project-context, structured-output, or routing workloads the Local AI Router actually needs.

The complete evaluation strategy therefore consists of:

```text
External standardized benchmarks
            +
Local AI Router project benchmarks
            +
Hardware/performance measurements
```

---

## 2. Benchmark suite structure

External benchmarks are divided into three execution classes.

### Development suite

A relatively small benchmark subset intended for frequent execution while developing the router.

Goals:

* catch obvious regressions;
* compare candidate configurations quickly;
* avoid hours of unnecessary inference;
* provide representative coverage across major capabilities.

The development suite may use deterministic subsets of larger benchmarks.

The exact selected case IDs must be versioned so different runs use the same cases.

### Periodic full suite

Larger standardized evaluations used when:

* introducing a new model;
* evaluating a new quantization;
* changing important runtime configuration;
* establishing a model capability profile;
* preparing a significant project release;
* periodically validating the production configuration.

These runs provide higher-confidence comparisons but may take substantially longer.

### Future / specialized suite

Benchmarks that depend on capabilities or infrastructure that are not yet implemented.

Examples include:

* tool calling;
* very large context windows;
* agentic behavior;
* specialized constrained decoding.

These benchmarks are documented now so the benchmark architecture can accommodate them later without requiring redesign.

---

# 3. Adopted benchmark overview

| Benchmark       | Primary capability               | Development     | Periodic full                   | Status                          |
| --------------- | -------------------------------- | --------------- | ------------------------------- | ------------------------------- |
| MMLU-Pro        | General knowledge and reasoning  | Yes             | Yes                             | Adopt                           |
| GPQA Diamond    | Difficult scientific reasoning   | Yes             | Yes                             | Adopt                           |
| IFEval          | Instruction following            | Yes             | Yes                             | Adopt                           |
| HumanEval+      | Code generation correctness      | Yes             | Yes                             | Adopt                           |
| MBPP+           | Practical Python coding          | Yes             | Yes                             | Adopt                           |
| LiveCodeBench   | Modern coding ability            | Optional subset | Yes                             | Adopt later in benchmark runner |
| LongBench v2    | Long-context reasoning/retrieval | Limited subset  | Yes where model context permits | Adopt                           |
| JSONSchemaBench | Structured JSON reliability      | Yes             | Yes                             | Adopt                           |
| BFCL            | Tool/function selection          | No              | Future                          | Deferred until tools exist      |

---

# 4. MMLU-Pro

## Purpose

MMLU-Pro provides a broad measure of general knowledge combined with reasoning.

It is more appropriate for this project than relying solely on the original MMLU because it increases task difficulty and reduces the effectiveness of random guessing.

## Characteristics

MMLU-Pro covers 14 broad domains and uses up to ten answer choices per question.

Representative domains include:

* computer science;
* mathematics;
* engineering;
* physics;
* chemistry;
* biology;
* economics;
* business;
* law;
* philosophy;
* psychology;
* health.

## Primary metric

```text
accuracy
```

Each case has a known correct answer.

No subjective LLM judge is required.

## Reference configuration

The initial standardized comparison configuration should use:

```text
evaluation split: test
shots: 5
metric: accuracy
answer format: benchmark-compatible multiple choice
```

When comparing against published scores, prompt construction and few-shot behavior must be compatible with the reference methodology.

## Local development subset

Create a deterministic balanced subset across domains.

Initial target:

```text
approximately 100–200 cases
```

The exact case IDs must be preserved.

The purpose of the development subset is rapid regression detection rather than claiming a full MMLU-Pro result.

## Full suite

Run the full benchmark when establishing or updating a serious model capability profile.

---

# 5. GPQA Diamond

## Purpose

GPQA Diamond evaluates difficult graduate-level scientific reasoning.

It complements MMLU-Pro by concentrating on questions intentionally designed to be difficult even for skilled non-experts.

## Domains

Primary domains include:

* physics;
* chemistry;
* biology.

## Primary metric

```text
accuracy
```

Each question has a known correct answer.

## Benchmark subset

Use:

```text
GPQA Diamond
```

rather than automatically running the entire GPQA collection.

Diamond is the most difficult commonly reported GPQA subset and is useful for distinguishing reasoning capability among stronger models.

## Development use

Because GPQA Diamond is relatively small compared with benchmarks such as MMLU-Pro, a substantial portion can be used in periodic evaluation.

A smaller fixed subset may be used for rapid development runs.

## Interpretation

GPQA should be treated primarily as a reasoning benchmark rather than a general knowledge benchmark.

Poor performance may indicate limitations in:

* scientific reasoning;
* multi-step reasoning;
* difficult problem decomposition.

It should not alone determine whether a model is suitable for normal conversational use.

---

# 6. IFEval

## Purpose

IFEval measures whether a model actually follows explicit instructions.

This is particularly relevant to the Local AI Router because applications require models to reliably obey:

* response formatting;
* output constraints;
* structural requirements;
* requested keywords;
* length constraints;
* machine-consumable instructions.

## Evaluation approach

IFEval uses instructions that can be checked programmatically.

Examples include requirements involving:

* number of paragraphs;
* required phrases;
* prohibited phrases;
* response structure;
* keyword usage;
* formatting constraints.

## Primary metrics

Preserve both:

```text
strict instruction-following accuracy
loose instruction-following accuracy
```

Where the selected evaluation implementation exposes prompt-level and instruction-level results, retain the individual metrics rather than collapsing them immediately into one number.

## Reference configuration

IFEval is normally evaluated without few-shot examples.

Use the benchmark's official deterministic checking logic wherever practical rather than reproducing the validators ourselves.

## Development use

IFEval is suitable for frequent evaluation because scoring does not require expensive model judges.

A deterministic subset may be used in the development suite.

---

# 7. HumanEval+

## Purpose

HumanEval+ measures whether generated Python solutions actually work.

The benchmark extends HumanEval with substantially more executable tests.

This is important because generated code may appear correct while failing edge cases not exercised by the original benchmark.

## Primary metric

The principal metric is:

```text
pass@1
```

For our initial deterministic local evaluation, one generated solution per task is preferred.

## Evaluation principle

Code is scored by execution.

```text
generated code
      ↓
isolated execution environment
      ↓
benchmark tests
      ↓
pass / fail
```

Executable test results should take precedence over subjective evaluation of whether code appears correct.

## Safety requirement

Generated benchmark code must eventually execute inside an isolated environment.

Do not execute arbitrary model-generated benchmark code directly against the main Local AI Router environment.

A containerized or otherwise sandboxed execution method should be used when Issue #9 implements the benchmark runner.

## Development use

A deterministic HumanEval+ subset may be run frequently.

The complete HumanEval+ suite should be included in periodic coding evaluation.

---

# 8. MBPP+

## Purpose

MBPP+ complements HumanEval+ with a larger collection of practical Python programming problems.

It evaluates somewhat different coding behavior from HumanEval+, so both benchmarks should be retained.

## Primary metric

```text
pass@1
```

## Evaluation method

Use the official EvalPlus execution and enhanced tests where practical.

HumanEval+ and MBPP+ results must remain separate.

Do not combine them into one undifferentiated "coding score" in raw storage.

The dashboard may later calculate a composite coding indicator while preserving both underlying scores.

## Development use

Use a deterministic subset during normal development.

Run the larger suite during serious model comparisons.

---

# 9. LiveCodeBench

## Purpose

LiveCodeBench provides a more contemporary coding evaluation and is intended to reduce benchmark contamination by continuously incorporating newer programming problems.

It also evaluates a broader coding skill set than simple code generation.

Possible scenarios include:

* code generation;
* code execution;
* test-output prediction;
* self-repair.

## Primary metrics

For code generation, preserve metrics such as:

```text
pass@1
pass@5
```

where applicable.

Our initial router comparison should prioritize:

```text
pass@1
```

because it more closely represents the normal case where the model must provide one useful answer.

## Dataset versioning requirement

LiveCodeBench evolves over time.

Every result must therefore record the exact release identifier.

Examples of release-style identifiers include:

```text
release_v1
release_v2
release_v3
...
```

Never compare two LiveCodeBench results as if they were identical experiments when the underlying release differs.

## Initial status

LiveCodeBench should not block the first benchmark-runner implementation.

Implement HumanEval+ and MBPP+ first because they offer a simpler coding-evaluation path.

Add LiveCodeBench after the base benchmark pipeline is functioning.

---

# 10. LongBench v2

## Purpose

LongBench v2 evaluates long-context understanding and reasoning using realistic multi-task problems.

This benchmark is particularly relevant to the Local AI Router because one of the project's goals is to determine practical context limits based on quality rather than advertised context-window size.

## Important distinction

A model supporting a configured context size does not prove that it can use all of that context reliably.

Long-context evaluation should measure whether the model can:

* find relevant information;
* preserve instructions;
* reason over distant information;
* avoid losing important details as context increases.

## Context requirements

LongBench v2 includes tasks across a very wide range of context lengths.

Not all cases will fit every local model configuration.

The benchmark runner must therefore record:

```text
case context length
configured model context limit
actual prompt token count
whether case was eligible to run
```

A case that exceeds a model's supported configuration should be recorded as:

```text
not eligible
```

rather than as an incorrect answer.

## Development use

Initially select cases that fit within the practical context configurations currently being tested.

Later Issue #11 will expand this into dedicated context-degradation experiments.

---

# 11. JSONSchemaBench

## Purpose

JSONSchemaBench evaluates structured-output behavior using real-world JSON schemas.

Reliable structured output is important because later Local AI Router components will require models to generate machine-consumable data for:

* routing decisions;
* tool calls;
* benchmark records;
* application actions;
* structured metadata.

## Dataset

JSONSchemaBench contains thousands of schemas across different domains and complexity levels.

The benchmark includes schema groups representing areas such as:

* GitHub-derived schemas;
* Kubernetes;
* APIs;
* function-call schemas;
* easy through difficult schema structures.

## Initial evaluation mode

Our initial interest is:

```text
native model structured-output reliability
```

rather than benchmarking constrained-decoding engines themselves.

For each selected schema:

```text
prompt
   ↓
model-generated JSON
   ↓
JSON parser
   ↓
schema validator
   ↓
valid / invalid
```

## Primary metrics

Store at minimum:

```text
JSON parse success rate
JSON Schema conformance rate
```

These measurements must remain separate.

A response can be syntactically valid JSON while still violating the required schema.

## Development use

Use a deterministic stratified subset across several schema-complexity levels.

There is no need to run every schema during normal development.

---

# 12. Berkeley Function Calling Leaderboard / BFCL

## Purpose

BFCL evaluates function and tool-calling behavior.

This will eventually become relevant when the Local AI Router implements its controlled tools/actions framework.

Potential capabilities include:

* selecting the correct function;
* selecting no function when appropriate;
* generating valid arguments;
* handling multiple functions;
* multi-turn tool interaction.

## Current status

```text
Deferred
```

Issue #7 documents BFCL so the benchmark architecture anticipates tool evaluation.

It should not be implemented until the Local AI Router has a stable tool schema and execution framework.

At that point BFCL can become an external reference alongside our project-specific tool-selection dataset.

---

# 13. Development benchmark suite v1

The first fast standardized suite should contain deterministic subsets from:

```text
MMLU-Pro
GPQA Diamond
IFEval
HumanEval+
MBPP+
JSONSchemaBench
```

LongBench v2 should be included only for cases that fit the currently tested context configurations.

LiveCodeBench is added after the initial benchmark runner works.

BFCL remains deferred.

A reasonable initial development-suite target is approximately:

```text
150–300 total cases
```

This number is an engineering target rather than a benchmark standard.

The objective is to provide broad enough coverage to catch meaningful differences while remaining practical to run repeatedly on one local GPU.

---

# 14. Periodic benchmark suite v1

When evaluating a serious model candidate, use substantially broader evaluations.

The periodic suite should include:

```text
MMLU-Pro
GPQA Diamond
IFEval
HumanEval+
MBPP+
LiveCodeBench
LongBench v2 where context permits
JSONSchemaBench representative/full selected profile
```

Not every benchmark must execute during one command initially.

The benchmark system should support suite composition so capability groups can be executed separately.

Examples:

```text
general-quality
reasoning
coding
instruction-following
structured-output
long-context
full-periodic
```

---

# 15. Reference scores versus locally measured scores

Published benchmark results must be stored separately from locally measured results.

Use the conceptual distinction:

```text
reference_result
```

versus:

```text
measured_result
```

A published score is not an expected unit-test value.

Differences can result from:

* different model revisions;
* different quantizations;
* different prompt templates;
* different few-shot examples;
* different reasoning settings;
* different context configuration;
* different sampling parameters;
* different inference engines;
* different benchmark versions;
* different evaluation-harness versions.

The benchmark database must preserve these differences.

---

# 16. Direct comparability

A local result may be labeled directly comparable to a reference result only when the important evaluation conditions are sufficiently compatible.

At minimum compare:

```text
benchmark name
benchmark version
dataset split
case selection
number of shots
prompt/template configuration
generation configuration
model version
quantization where applicable
scoring implementation
```

If those differ materially, the reference score may still be displayed for context but must be labeled:

```text
not directly comparable
```

---

# 17. Benchmark provenance

Every external benchmark definition should eventually record provenance metadata.

At minimum:

```text
benchmark_name
benchmark_version
dataset_version
dataset_source
evaluation_harness
evaluation_harness_version
case_id
license
retrieval/download date
```

Where a benchmark repository does not publish formal releases, preserve the Git commit SHA used for evaluation.

This is particularly important for continuously updated benchmarks.

---

# 18. Dataset integrity

External benchmark data must not be modified silently.

If we create a development subset, preserve:

```text
source benchmark
source version
original case IDs
subset-selection method
subset version
```

A fixed development subset should not randomly choose different questions on every run.

Random sampling may be used to construct a subset initially, but once selected, the exact IDs must be stored and versioned.

---

# 19. Benchmark contamination

Public benchmark questions may have appeared in model training data.

A high benchmark result does not necessarily prove generalized capability.

For this reason:

* use multiple benchmarks for important capabilities;
* include newer benchmarks such as LiveCodeBench;
* maintain Local AI Router-specific unseen tests;
* avoid choosing models from one leaderboard result alone.

External benchmarks provide useful evidence, not absolute proof of model quality.

---

# 20. Scoring storage

Do not store only the final benchmark percentage.

For every benchmark run preserve applicable lower-level information.

Example:

```text
benchmark:
    mmlu_pro

case:
    computer_science_00123

expected_answer:
    F

model_answer:
    F

correct:
    true

latency:
    ...

tokens:
    ...
```

For code:

```text
benchmark:
    humaneval_plus

case:
    HumanEval/42

generated_code:
    ...

tests_passed:
    true

execution_details:
    ...
```

For structured output:

```text
benchmark:
    json_schema_bench

case:
    ...

json_parse_success:
    true

schema_validation_success:
    false

validation_errors:
    ...
```

This case-level data will allow later re-analysis without losing information behind an aggregate score.

---

# 21. Performance telemetry

External benchmark quality scores should be accompanied by our own locally measured performance telemetry.

Where available record:

```text
total latency
time to first token
prompt tokens
prompt evaluation duration
prompt tokens/sec
output tokens
output generation duration
output tokens/sec
model load time
peak VRAM
peak system RAM
```

Performance telemetry is specific to our hardware/runtime environment and must not be treated as equivalent to performance measurements published from unrelated hardware.

---

# 22. Current baseline hardware

The initial benchmark hardware profile is the Local AI Router development workstation.

Primary inference hardware:

```text
GPU:
    NVIDIA GeForce RTX 5060 Ti

VRAM:
    16 GB
```

Additional hardware and software metadata will be captured automatically once the benchmark runner is implemented.

Benchmark results produced after significant hardware changes must use a different hardware profile.

---

# 23. Integration strategy

The first implementation should not rewrite every external benchmark evaluator.

Where a trustworthy maintained evaluation harness already exists, prefer integrating its evaluator or importing its machine-readable output.

Conceptually:

```text
External benchmark
        ↓
Official/established evaluator
        ↓
Raw result
        ↓
Local AI benchmark adapter
        ↓
Normalized benchmark record
        ↓
PostgreSQL
```

This reduces the risk that our own reimplementation changes benchmark semantics and makes published comparisons invalid.

---

# 24. Benchmark adapters

Each external benchmark will eventually have an adapter responsible for translating benchmark-specific results into the Local AI Router benchmark schema.

Example future structure:

```text
benchmarking/
├── adapters/
│   ├── mmlu_pro.py
│   ├── gpqa.py
│   ├── ifeval.py
│   ├── evalplus.py
│   ├── livecodebench.py
│   ├── longbench.py
│   └── jsonschema.py
```

These adapters should not erase benchmark-specific fields.

The database should support:

```text
normalized common metrics
        +
benchmark-specific raw metadata
```

---

# 25. Initial implementation order

Recommended implementation sequence:

```text
1. MMLU-Pro
2. GPQA Diamond
3. IFEval
4. HumanEval+
5. MBPP+
6. JSONSchemaBench
7. LongBench v2
8. LiveCodeBench
9. BFCL after tool support exists
```

This order begins with deterministic question-answer scoring, then instruction following, executable coding, structured output, long context, and finally more specialized capabilities.

---

# 26. Relationship to Local AI Router benchmarks

The external suite does not directly test several important Local AI Router requirements.

Custom tests will still be required for:

* FastAPI development;
* Local AI Router architecture reasoning;
* PostgreSQL/database design;
* debugging project code;
* project identification;
* project-context retrieval;
* memory selection;
* router decision accuracy;
* retrieval relevance;
* model-selection decisions;
* reasoning-effort decisions;
* project isolation;
* real Local AI development workflows.

These tests form the Local AI Router benchmark suite and complement the external suite.

---

# 27. Version-1 benchmark policy

A model should not be selected for a router role from one benchmark score.

Model capability decisions should consider:

```text
multiple relevant quality benchmarks
+
Local AI Router workload results
+
latency
+
throughput
+
VRAM cost
+
context behavior
+
reliability
```

For example, selection of a coding model should eventually consider:

```text
HumanEval+
MBPP+
LiveCodeBench
Local AI Router coding suite
latency
tokens/sec
VRAM usage
```

rather than simply choosing whichever model has the highest HumanEval+ score.

---

# 28. Version-1 adopted suite

The Local AI Router external benchmark suite v1 therefore adopts:

## Active initial benchmarks

```text
MMLU-Pro
GPQA Diamond
IFEval
HumanEval+
MBPP+
JSONSchemaBench
```

## Context-specific benchmark

```text
LongBench v2
```

## Secondary coding benchmark

```text
LiveCodeBench
```

Add after the initial benchmark runner is operational.

## Deferred tool benchmark

```text
BFCL
```

Enable after the controlled tools/actions framework exists.

---

# 29. Design principle

External benchmarks provide a common measuring stick.

Local project benchmarks tell us whether a model is actually useful for this system.

Performance telemetry tells us whether that usefulness is affordable on the target hardware.

The Local AI Router should make model-selection decisions from all three forms of evidence rather than optimizing for a single leaderboard score.

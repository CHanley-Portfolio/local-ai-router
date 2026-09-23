"""
Structural validation tests for Local AI Routr benchmark datasets.

These tests do not execute AI inference.

Their purpose is to ensure that benchmark definitions remain internally consistent as the benchmark library grows.
A malformed dataset should fail CI before an expensive benchmark run discovers teh problem.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

LOCAL_BENCHMARK_DATASET = PROJECT_ROOT / "benchmarks" / "datasets" / "local_ai_router_v1.json"

BENCHMARK_FIXTURE_DIRECTORY = PROJECT_ROOT / "benchmarks" / "fixtures"


def load_local_benchmark_cases() -> list[dict]:
    """
    Load the version-1 Local AI Router benchmark dataset.

    Returns:
        list[dict]:
            Parsed benchmark case definitions.

    Raises:
        json.JSONDecodeError:
            Raised automatically if the dataset contains invalid JSON.

        FileNotFoundError:
            Raised if the benchmark dataset does not exist.
    """

    with LOCAL_BENCHMARK_DATASET.open(
        mode="r",
        encoding="utf-8",
    ) as benchmark_file:
        return json.load(benchmark_file)


def test_local_benchmark_dataset_is_valid_json_list() -> None:
    """
    Verify that the benchmark dataset can be parsed and has a list root.

    a syntax error or accidental change to the top-level structure
    would make the future benchmark runner unable to load the suite.
    """

    benchmark_cases = load_local_benchmark_cases()

    assert isinstance(benchmark_cases, list)
    assert benchmark_cases


def test_local_benchmark_case_ids_are_unique() -> None:
    """
    Ensure every benchmark case has a unique persistant identifier.

    Case IDs will eventually be references by PostgreSQL benchmark results,
    so duplicate IDs would make historical results ambiguous.
    """

    benchmark_cases = load_local_benchmark_cases()

    case_ids = [benchmark_case["case_id"] for benchmark_case in benchmark_cases]

    assert len(case_ids) == len(set(case_ids))


def test_local_benchmark_cases_contain_required_fields() -> None:
    """
    Verify that every benchmark definition contains the common metadata needed by the future benchmark runner and database.
    """

    benchmark_cases = load_local_benchmark_cases()

    required_fields = {
        "case_id",
        "case_version",
        "evaluation_target",
        "category",
        "tags",
        "prompt",
        "context_fixture",
        "scoring_method",
        "critical",
    }

    for benchmark_case in benchmark_cases:
        assert required_fields.issubset(benchmark_case)


def test_local_benchmark_case_values_are_supported() -> None:
    """
    Verify important controlled fields use recognized values.

    Central validation prevents small spelling variations from creating
    accidental new benchmark categories or evaluation-target types
    """

    benchmark_cases = load_local_benchmark_cases()

    supported_evaluation_targets = {
        "model",
        "router",
    }

    supported_scoring_methods = {
        "exact",
        "exact_with_explanation",
        "rubric",
    }

    for benchmark_case in benchmark_cases:
        assert benchmark_case["evaluation_target"] in supported_evaluation_targets
        assert benchmark_case["scoring_method"] in supported_scoring_methods

        assert isinstance(benchmark_case["case_version"], int)
        assert benchmark_case["case_version"] >= 1

        assert isinstance(benchmark_case["tags"], list)
        assert benchmark_case["tags"]

        assert isinstance(benchmark_case["critical"], bool)


def test_all_referenced_context_fixtures_exist() -> None:
    """
    Verify that every reference benchmark fixture exists.

    A benchmark case may omit context by setting context_fixture to null.
    When a fixture name is supplied, that file must exist in the fixtue directory.
    """

    benchmark_cases = load_local_benchmark_cases()

    for benchmark_case in benchmark_cases:
        context_fixture = benchmark_case["context_fixture"]

        if context_fixture is None:
            continue

        fixture_path = BENCHMARK_FIXTURE_DIRECTORY / context_fixture

        assert fixture_path.is_file(), (
            f"Benchmark case {benchmark_case['case_id']} references "
            f"missing fixture: {context_fixture}"
        )


def test_router_benchmark_cases_define_expected_route() -> None:
    """
    Ensure router-target cases declare to route expected by the benchmark.

    Model-targeted cases do not require expected_route_mode
    because they are scored against generated answers instead
    """

    benchmark_cases = load_local_benchmark_cases()

    for benchmark_case in benchmark_cases:
        if benchmark_case["evaluation_target"] != "router":
            continue

        assert benchmark_case["expected_route_mode"] in {
            "fast",
            "reasoning",
        }


def test_model_benchmark_cases_define_scoring_expectations() -> None:
    """
    Ensure model-targeted cases contain information that can atually score their generated answers.

    Rubric cases require expected_criteria.

    Exact-with-explanation cases require both expected answer and explicit evaluation criteria.
    """

    benchmark_cases = load_local_benchmark_cases()

    for benchmark_case in benchmark_cases:
        if benchmark_case["evaluation_target"] != "model":
            continue

        scoring_method = benchmark_case["scoring_method"]

        if scoring_method == "rubric":
            assert benchmark_case.get("expected_criteria")

        if scoring_method == "exact_with_explanation":
            assert benchmark_case.get("expected_answer")
            assert benchmark_case.get("expected_criteria")

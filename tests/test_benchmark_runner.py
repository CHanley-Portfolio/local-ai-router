"""
Unit tests for benchmark execution orchestration.

These tests use fake inference executors so BenchmarkRunner behavior can be
validated without Ollama, a GPU, or a loaded model.
"""

import asyncio
from dataclasses import FrozenInstanceError

import pytest

from local_ai_router.benchmarking import (
    BenchmarkCaseRequest,
    BenchmarkRunner,
)
from local_ai_router.inference import InferenceRequest, InferenceResult


class SuccessfulFakeInferenceExecutor:
    """
    Deterministic fake inference backend used by BenchmarkRunner tests.
    """

    def __init__(
        self,
        inference_result: InferenceResult,
    ) -> None:
        self.inference_result = inference_result
        self.received_request: InferenceRequest | None = None

    async def chat(
        self,
        inference_request: InferenceRequest,
    ) -> InferenceResult:
        """
        Record the request and return the configured result.
        """

        self.received_request = inference_request
        return self.inference_result


class FailingFakeInferenceExecutor:
    """
    Fake inference backend that always raises an execution error.
    """

    async def chat(
        self,
        inference_request: InferenceRequest,
    ) -> InferenceResult:
        """
        Simulate an inference backend failure.
        """

        raise RuntimeError("Synthetic inference failure.")


class SequencedFakeInferenceExecutor:
    """
    Fake executor that can succeed or fail based on the incoming prompt.

    This allows suite tests to prove that one failed case does not prevent
    later benchmark cases from executing.
    """

    def __init__(self) -> None:
        self.received_requests: list[InferenceRequest] = []

    async def chat(
        self,
        inference_request: InferenceRequest,
    ) -> InferenceResult:
        """
        Return deterministic results or raise for the synthetic failure case.
        """

        self.received_requests.append(inference_request)

        if inference_request.user_message == "fail":
            raise RuntimeError("Synthetic suite failure.")

        return InferenceResult(
            model_name=inference_request.model_name,
            response_text=f"response:{inference_request.user_message}",
        )


def test_benchmark_runner_executes_case_through_inference_contract() -> None:
    """
    Verify BenchmarkRunner sends the normalized request to its executor.

    Successful execution must preserve the resulting InferenceResult without
    requiring BenchmarkRunner to understand backend-specific response data.
    """

    inference_request = InferenceRequest(
        model_name="test-model",
        user_message="Return exactly the word ready.",
        thinking_enabled=False,
    )

    expected_inference_result = InferenceResult(
        model_name="test-model",
        response_text="ready",
        total_duration_ns=1_000_000,
        output_token_count=1,
    )

    fake_executor = SuccessfulFakeInferenceExecutor(expected_inference_result)

    benchmark_runner = BenchmarkRunner(fake_executor)

    execution = asyncio.run(
        benchmark_runner.execute_case(
            benchmark_case_id=123,
            inference_request=inference_request,
        )
    )

    assert fake_executor.received_request is inference_request

    assert execution.benchmark_case_id == 123
    assert execution.status == "completed"

    assert execution.inference_result is expected_inference_result

    assert execution.error_type is None
    assert execution.error_message is None

    assert execution.started_at.tzinfo is not None
    assert execution.completed_at.tzinfo is not None
    assert execution.completed_at >= execution.started_at


def test_benchmark_runner_retains_inference_failure_diagnostics() -> None:
    """
    Verify one inference failure becomes benchmark result data.

    The runner should not raise the backend exception through the entire suite.
    Instead, it retains useful diagnostic information so the failed case can
    eventually be persisted while other cases continue executing.
    """

    inference_request = InferenceRequest(
        model_name="test-model",
        user_message="Test prompt",
        thinking_enabled=False,
    )

    benchmark_runner = BenchmarkRunner(FailingFakeInferenceExecutor())

    execution = asyncio.run(
        benchmark_runner.execute_case(
            benchmark_case_id=456,
            inference_request=inference_request,
        )
    )

    assert execution.benchmark_case_id == 456
    assert execution.status == "failed"

    assert execution.inference_result is None

    assert execution.error_type == "RuntimeError"
    assert execution.error_message == "Synthetic inference failure."

    assert execution.completed_at >= execution.started_at


def test_benchmark_case_execution_is_immutable() -> None:
    """
    Verify an execution record cannot be modified after it is created.

    Benchmark evidence should remain stable after execution so later scoring
    and persistence cannot accidentally rewrite the observed result.
    """

    inference_request = InferenceRequest(
        model_name="test-model",
        user_message="Test prompt",
        thinking_enabled=False,
    )

    inference_result = InferenceResult(
        model_name="test-model",
        response_text="answer",
    )

    benchmark_runner = BenchmarkRunner(SuccessfulFakeInferenceExecutor(inference_result))

    execution = asyncio.run(
        benchmark_runner.execute_case(
            benchmark_case_id=789,
            inference_request=inference_request,
        )
    )

    with pytest.raises(FrozenInstanceError):
        execution.status = "failed"  # type: ignore[misc]

def test_benchmark_runner_executes_suite_in_request_order() -> None:
    """
    Verify suite orchestration preserves benchmark-case execution order.
    """

    fake_executor = SequencedFakeInferenceExecutor()
    benchmark_runner = BenchmarkRunner(fake_executor)

    first_request = BenchmarkCaseRequest(
        benchmark_case_id=101,
        inference_request=InferenceRequest(
            model_name="test-model",
            user_message="first",
            thinking_enabled=False,
        ),
    )

    second_request = BenchmarkCaseRequest(
        benchmark_case_id=102,
        inference_request=InferenceRequest(
            model_name="test-model",
            user_message="second",
            thinking_enabled=False,
        ),
    )

    summary = asyncio.run(
        benchmark_runner.execute_suite(
            benchmark_suite_id=10,
            case_requests=(
                first_request,
                second_request,
            ),
        )
    )

    assert summary.benchmark_suite_id == 10
    assert summary.status == "completed"

    assert summary.total_case_count == 2
    assert summary.completed_case_count == 2
    assert summary.failed_case_count == 0

    assert [
        execution.benchmark_case_id
        for execution in summary.case_executions
    ] == [
        101,
        102,
    ]

    assert [
        request.user_message
        for request in fake_executor.received_requests
    ] == [
        "first",
        "second",
    ]


def test_benchmark_runner_continues_after_case_failure() -> None:
    """
    Verify one failed benchmark case does not terminate the suite.

    The failed execution should remain in the summary while later cases are
    still attempted.
    """

    fake_executor = SequencedFakeInferenceExecutor()
    benchmark_runner = BenchmarkRunner(fake_executor)

    summary = asyncio.run(
        benchmark_runner.execute_suite(
            benchmark_suite_id=20,
            case_requests=(
                BenchmarkCaseRequest(
                    benchmark_case_id=201,
                    inference_request=InferenceRequest(
                        model_name="test-model",
                        user_message="first",
                        thinking_enabled=False,
                    ),
                ),
                BenchmarkCaseRequest(
                    benchmark_case_id=202,
                    inference_request=InferenceRequest(
                        model_name="test-model",
                        user_message="fail",
                        thinking_enabled=False,
                    ),
                ),
                BenchmarkCaseRequest(
                    benchmark_case_id=203,
                    inference_request=InferenceRequest(
                        model_name="test-model",
                        user_message="third",
                        thinking_enabled=False,
                    ),
                ),
            ),
        )
    )

    assert summary.status == "completed_with_failures"

    assert summary.total_case_count == 3
    assert summary.completed_case_count == 2
    assert summary.failed_case_count == 1

    assert len(summary.case_executions) == 3

    failed_execution = summary.case_executions[1]

    assert failed_execution.benchmark_case_id == 202
    assert failed_execution.status == "failed"
    assert failed_execution.error_type == "RuntimeError"
    assert (
        failed_execution.error_message
        == "Synthetic suite failure."
    )

    # Most importantly, the third request was still executed.
    assert [
        request.user_message
        for request in fake_executor.received_requests
    ] == [
        "first",
        "fail",
        "third",
    ]


def test_benchmark_runner_rejects_empty_suite() -> None:
    """
    Verify suite execution cannot silently produce a meaningless empty run.
    """

    benchmark_runner = BenchmarkRunner(
        SequencedFakeInferenceExecutor()
    )

    with pytest.raises(
        ValueError,
        match="must contain at least one case request",
    ):
        asyncio.run(
            benchmark_runner.execute_suite(
                benchmark_suite_id=30,
                case_requests=(),
            )
        )


def test_benchmark_run_summary_is_immutable() -> None:
    """
    Verify completed suite summaries cannot be mutated accidentally.
    """

    benchmark_runner = BenchmarkRunner(
        SequencedFakeInferenceExecutor()
    )

    summary = asyncio.run(
        benchmark_runner.execute_suite(
            benchmark_suite_id=40,
            case_requests=(
                BenchmarkCaseRequest(
                    benchmark_case_id=401,
                    inference_request=InferenceRequest(
                        model_name="test-model",
                        user_message="test",
                        thinking_enabled=False,
                    ),
                ),
            ),
        )
    )

    with pytest.raises(FrozenInstanceError):
        summary.status = "completed_with_failures"  # type: ignore[misc]
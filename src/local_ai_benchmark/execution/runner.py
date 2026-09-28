"""
Benchmark execution orchestration.

BenchmarkRunner coodinates benchmark inference without depending directly on a specific backend such as Ollama.

Databse persistence and quality scoring will be added as seperate responsibilities
rather than embeddding every benchmark concern inside this class.
"""

from datetime import datetime, timezone

from local_ai_inference import InferenceRequest

from .data import (
    BenchmarkCaseExecution,
    BenchmarkCaseRequest,
    BenchmarkRunSummary,
)
from .inference_executor import InferenceExecutor


class BenchmarkRunner:
    """
    Execute benchmark cases through a normalized inference interface.

    BenchmarkRunner depends on InferenceExecutor rather than OllamaClient.

    This allows:
        - production execution through OllamaCLient;
        - future executions through another inference backend;
        - deterministic tests through fake inference executors.

    the runner currently handles only inference execution.

    future benchmark stages will add:
        - suite orchestration;
        - quality scoring;
        - PostgreSQL persistence;
        - run summaries;
        - resource measusrments;
        - historical comparison.
    """

    def __init__(self, inference_executor: InferenceExecutor) -> None:
        """
        Create a benchmark runner.

        Args:
            inference_executor:
                Object capable of accepting an InferenceRequest and returning an InferenceResult.

                OllamaClient satisfies this contract, but BenchmarkRunner does not depend on OllamaClient specifically.
        """

        self._inference_executor = inference_executor

    async def execute_case(
        self, *, benchmark_case_id: int, inference_request: InferenceRequest
    ) -> BenchmarkCaseExecution:
        """
        Execute one benchmark case.

        Args:
            benchmark_case_id:
                Persistent benchmark-case identifier.

            inference_request:
                Fully normalized inference request describing the model, prompt, reasoning configuration and generation settings.

        Returns:
            BenchmarkCaseExecution:
                Structured execution result.

                Successful inference contains and InferenceResult.

                Failed inference retains error type and message instead of raising through the entire benchmark suite.

        design:
            Individual benchmark-case failures should not automatically abort and entire benchmark suite.

            Capturing the failure as data allows later suite orchestration to
            continue executing remainigng cases while preserving diagnotics.
        """

        started_at = datetime.now(timezone.utc)

        try:
            inference_result = await self._inference_executor.chat(inference_request)

        except Exception as exc:
            # Benchmark failures are retained as structured data.
            #
            # We intentionally catch Exception rather than BaseException.
            # Process-level events such as KeyboardInterrupt and SystemExit
            # should still be allowed to terminate execution normally.
            completed_at = datetime.now(timezone.utc)

            return BenchmarkCaseExecution(
                benchmark_case_id=benchmark_case_id,
                status="failed",
                started_at=started_at,
                completed_at=completed_at,
                inference_result=None,
                error_type=type(exc).__name__,
                error_message=str(exc),
            )

        completed_at = datetime.now(timezone.utc)

        return BenchmarkCaseExecution(
            benchmark_case_id=benchmark_case_id,
            status="completed",
            started_at=started_at,
            completed_at=completed_at,
            inference_result=inference_result,
        )

    async def execute_suite(
        self, *, benchmark_suite_id: int, case_requests: tuple[BenchmarkCaseRequest, ...]
    ) -> BenchmarkRunSummary:
        """
        Execute every case in one benchmark suite.

        Args:
            benchmark_suite_id:
                Persistent identifier of the suite being executed.

            case_requests:
                Ordered benchmark case requests.

                Tuple order defines execution order and is preserved in the
                resulting BenchmarkRunSummary.

        Returns:
            BenchmarkRunSummary:
                Machine-readable summary containing every individual execution
                result and aggregate execution counts.

        Raises:
            ValueError:
                Raised when no benchmark cases are supplied.

        Design:
            Individual case failures do not abort suite execution.

            ``execute_case`` converts backend exceptions into structured failed
            executions, allowing this method to continue to later cases.

            Quality scoring is deliberately not performed here yet.
        """

        if not case_requests:
            raise ValueError("A benchmark suite must contain at least one case request.")

        started_at = datetime.now(timezone.utc)

        case_executions: list[BenchmarkCaseExecution] = []

        for case_request in case_requests:
            case_execution = await self.execute_case(
                benchmark_case_id=case_request.benchmark_case_id,
                inference_request=case_request.inference_request,
            )

            case_executions.append(case_execution)

        completed_at = datetime.now(timezone.utc)

        completed_case_count = sum(
            case_execution.status == "completed" for case_execution in case_executions
        )

        failed_case_count = sum(
            case_execution.status == "failed" for case_execution in case_executions
        )

        run_status = "completed" if failed_case_count == 0 else "completed_with_failures"

        return BenchmarkRunSummary(
            benchmark_suite_id=benchmark_suite_id,
            status=run_status,
            started_at=started_at,
            completed_at=completed_at,
            case_executions=tuple(case_executions),
            total_case_count=len(case_executions),
            completed_case_count=completed_case_count,
            failed_case_count=failed_case_count,
        )

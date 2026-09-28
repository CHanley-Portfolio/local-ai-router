"""
Machine-readable summary of one benchmark-suite execution.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from .benchmark_case_execution import BenchmarkCaseExecution

BenchmarkRunExecutionStatus = Literal[
    "completed",
    "completed_with_failures",
]


@dataclass(frozen=True)
class BenchmarkRunSummary:
    """
    Summarize execution of one benchmark suite.

    This object describes execution behavior only.

    A case with ``status="completed"`` successfully produced a model response,
    but that response may still fail later quality scoring.

    Attributes:
        benchmark_suite_id:
            Persistent identifier of the benchmark suite.

        status:
            Overall execution state.

            ``completed`` means every case completed inference.

            ``completed_with_failures`` means suite orchestration finished,
            but at least one individual case failed during inference.

        started_at:
            UTC timestamp recorded before the first case begins.

        completed_at:
            UTC timestamp recorded after all cases have been attempted.

        case_executions:
            Ordered immutable collection of all case execution outcomes.

        total_case_count:
            Number of cases attempted.

        completed_case_count:
            Number of cases whose inference completed successfully.

        failed_case_count:
            Number of cases that failed during inference.
    """

    benchmark_suite_id: int
    status: BenchmarkRunExecutionStatus

    started_at: datetime
    completed_at: datetime

    case_executions: tuple[BenchmarkCaseExecution, ...]

    total_case_count: int
    completed_case_count: int
    failed_case_count: int

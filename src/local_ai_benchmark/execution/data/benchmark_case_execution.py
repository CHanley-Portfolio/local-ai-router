"""
Execution result for one benchmark case.

This object represents what happened while attempting a single benchamark case
before database persistence or quality scoring is applied.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from local_ai_inference import InferenceResult

BenchmarkCaseExecutionStatus = Literal[
    "completed",
    "failed",
]


@dataclass(frozen=True)
class BenchmarkCaseExecution:
    """
    Represent the execution outcome of one benchamark case.

    Attributes:
        benchmark_case_id:
            Database identifier of the benchmark case being executed.

        status:
            Execution-level state.

            'completed' means inference returned normally.

            'failed' means inference could not complete and diagnostic information was captured instead.

            This status does not yet indicate whether the model's answer was  correct.
            Quality scoring is a separate benchmark stage.

        started_at:
            UTC timestamp immediately before inference execution begins.

        completed_at:
            UTC timestamp recorded when execution finishes or fails.

        inference_result:
            Normalized mondel output and telemetry when inference succeeds.

            Failed executions leave this as 'None'.

        error_type:
            Exception class name when execution fails.

        error_message:
            Human_readable exception messafe retained for diagnostics.
    """

    benchmark_case_id: int
    status: BenchmarkCaseExecutionStatus

    started_at: datetime
    completed_at: datetime

    inference_result: InferenceResult | None = None

    error_type: str | None = None
    error_message: str | None = None

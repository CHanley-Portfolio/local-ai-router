"""
Execution request for one benchmark case.

BenchmarkCaseRequest connects a persistent benchmark-case identifier to the
normalized inference request that should be executed for that case.
"""

from dataclasses import dataclass

from local_ai_inference import InferenceRequest


@dataclass(frozen=True)
class BenchmarkCaseRequest:
    """
    Describe one benchmark case that should be executed.

    Attributes:
        benchmark_case_id:
            Persistent identifier of the benchmark case.

        inference_request:
            Fully normalized inference request containing the model, prompt,
            reasoning setting, and generation configuration.
    """

    benchmark_case_id: int
    inference_request: InferenceRequest

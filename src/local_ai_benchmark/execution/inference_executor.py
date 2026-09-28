"""
Inference execution contract used by benchmark infrastructure.

The benchmark runner must not depend directly on OllamaClient or any other specific inference backend.

Any inference adapter that implements the required 'chat' method can satisfy
this protocol through Python's structural typing.
"""

from typing import Protocol

from local_ai_inference import InferenceRequest, InferenceResult


class InferenceExecutor(Protocol):
    """
    Define the inference behavior required by BenchmarkRunner.

    The protocol deliberately describes behavior rather than a concrete class.

    OllamaClient already satisfies this contract because it exposes:
        async chat(InferenceRequest) -> InferenceResult

    Future inference backends can satisfy the same protocol without inheriting
    from OllamaClient or changing benchmark-runner code.
    """

    async def chat(self, inference_request: InferenceRequest) -> InferenceResult:
        """
        Execute one normalized inference request.

        Args:
            inference_request:
                Backend-independence inference configuration and prompt.

        Returns:
            InferenceResult:
                Normalized model output and available performance telemetry.
        """

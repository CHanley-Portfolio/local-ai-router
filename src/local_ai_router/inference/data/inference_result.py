"""
Backend-independent inference result data.

Inference backend expose different response formats.
InferenceResult provides teh stable representation used by the Local AI Router, benchmark runner,
API and persistence layers.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class InferenceResult:
    """
    Represent one complete model inference operation.

    Timing values are stored in nanoseconds because Ollama reports its native
    timing metrics in nanoseconds and retaining the original precision avoids
    lossy conversions before benchmark persistence.

    Attributes:
        model_name:
            Model reported by the inference backend.

        response_text:
            Final tetual model response.

        total_duration_ns:
            Complete backend request duration when available.

        model_load_duration_ns:
            Time spent loading or preparing the model when available.

        prompt_token_count:
            Number of input/prompt tokens processed.

        prompt_eval_duration_ns:
            Time spent processing prompt tokens.

        output_token_count:
            Number of generated output tokens.

        output_eval_duration_ns:
            Time spent generating output tokens.

        backend_metrics:
            Additional backend-specific metrics preserved for diagnostics or
            future analysis without coupling callers to raw backend JSON.
    """

    model_name: str
    response_text: str

    total_duration_ns: int | None = None
    model_load_duration_ns: int | None = None

    prompt_token_count: int | None = None
    prompt_eval_duration_ns: int | None = None

    output_token_count: int | None = None
    output_eval_duration_ns: int | None = None

    backend_metrics: dict[str, Any] | None = None

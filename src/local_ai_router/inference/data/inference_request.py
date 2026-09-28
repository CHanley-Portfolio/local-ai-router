"""
Backend-independent inference request data.

InferenceRequest represents the model execution settings understood by the Local AI Router itself.

Backend adapters such as OllamaClient are responsible for translating
these application-level setting into backend-specific request payloads.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class InferenceRequest:
    """
    Describe one model inference operation.

    Attributes:
        model_name:
            Backend model identifier that should execute the request.

        user_message:
            Prompt supplied to the model.

        thinking_enabled:
            Whether reasoning/thinking behavior should be requested.

        temperature:
            Optional sampling temperature.

        top_p:
            Optional nucleus-sampling probability.

        seed:
            Optional deterministic generation seed.

        max_output_tokens:
            Optional maximum number of generated tokens.

        backend_options:
            Additional backend-specific configuration that does not yet have a normalized Local AI Router field.

            This escape hatch should be used sparingly.
            Common settings should eventually becaome explicit fields instead of accumulating here.
    """

    model_name: str
    user_message: str
    thinking_enabled: bool

    temperature: Decimal | None = None
    top_p: Decimal | None = None
    seed: int | None = None
    max_output_tokens: int | None = None

    backend_options: dict[str, Any] | None = None

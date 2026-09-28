"""
Shared inference data contracts used across Local AI Platform services.
"""

from .inference_request import InferenceRequest as InferenceRequest
from .inference_result import InferenceResult as InferenceResult

__all__ = [
    "InferenceRequest",
    "InferenceResult",
]

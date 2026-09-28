"""
Shared inference data contracts.
"""

from .inference_request import InferenceRequest
from .inference_result import InferenceResult

__all__ = [
    "InferenceRequest",
    "InferenceResult",
]

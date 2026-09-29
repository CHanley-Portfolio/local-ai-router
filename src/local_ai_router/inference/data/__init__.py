"""
Backend-independent inference data contracts for the Local AI Router.
"""

from .inference_request import InferenceRequest as InferenceRequest
from .inference_result import InferenceResult as InferenceResult

__all__ = [
    "InferenceRequest",
    "InferenceResult",
]

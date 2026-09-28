"""
Shared inference capability for Local AI Platform services.

This package owns backend-independent inference contracts and inference
backend adapters that are shared by services such as the runtime router and
benchmark service.

Neither the router nor benchmark service should own these contracts directly.
"""

from .data import InferenceRequest as InferenceRequest
from .data import InferenceResult as InferenceResult
from .ollama_client import OllamaClient as OllamaClient

__all__ = [
    "InferenceRequest",
    "InferenceResult",
    "OllamaClient",
]

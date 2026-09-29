"""
Inference contracts and backend adapters owned by the Local AI Router.

The router exposes backend-independent request and result objects so routing
and API code do not depend on Ollama-specific payload structures.
"""

from .data import InferenceRequest as InferenceRequest
from .data import InferenceResult as InferenceResult
from .ollama_client import OllamaClient as OllamaClient

__all__ = [
    "InferenceRequest",
    "InferenceResult",
    "OllamaClient",
]

"""
Application configuration loaded from environment variables.

Configuration values that are safe to have development defaults may provide them here.
Sensetive values, such as database passwords, must be supplied through the environment
and are never hard-coded into the repository.
"""

import os

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://127.0.0.1:11434",
)

DEFAULT_MODEL = os.getenv(
    "DEFAULT_MODEL",
    "qwen3.5-9b-32k",
)

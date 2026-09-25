"""
Application configuration loaded from environment variables.

Configuration values that are safe to have development defaults may provide them here.
Sensetive values, such as database passwords, must be supplied through the environment
and are never hard-coded into the repository.
"""

import os
from dataclasses import dataclass


OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://127.0.0.1:11434",
)

DEFAULT_MODEL = os.getenv(
    "DEFAULT_MODEL",
    "qwen3.5-9b-32k",
)


@dataclass(frozen=True)
class DatabaseSettings:
    """
    Connection settings required to connect to PostgreSQL.

    Attributes:
        host:
            PostgreSQL server hostname or IP address.

        port:
            TCP port used by PostgreSQL.

        database_name:
            Name of the PostgreSQL database teh application should use.

        username:
            PostgreSQL login role used by the application.

        password:
            Password belonging to the PostgreSQL application role.
    """

    host: str
    port: int
    database_name: str
    username: str
    password: str


def get_database_settings() -> DatabaseSettings:
    """
    Load PostgreSQL connection settings from environment variables.

    Most local-development values have sensible project defaults because they are not secrets.
    The password intentionally has no default and must be supplied explicitly.

    Returns:
        DatabaseSettings:
            Immutable database connection configuration.

    Raises:
        RuntimeError:
            Raised when LOCAL_AI_ROUTER_DB_PASSWORD has not been provided.
    """
    database_password = os.getenv("LOCAL_AI_ROUTER_DB_PASSWORD")

    if not database_password:
        raise RuntimeError("LOCAL_AI_ROUTER_DB_PASSWORD environment variable is required.")

    return DatabaseSettings(
        host=os.getenv("LOCAL_AI_ROUTER_DB_HOST", "127.0.0.1"),
        port=int(os.getenv("LOCAL_AI_ROUTER_DB_PORT", "5432")),
        database_name=os.getenv("LOCAL_AI_ROUTER_DB_NAME", "local_ai_router"),
        username=os.getenv("LOCAL_AI_ROUTER_DB_USER", "local_ai_router_app"),
        password=database_password,
    )

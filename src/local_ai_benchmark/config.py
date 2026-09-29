"""
Configuration owned by the Benchmark Service.

Benchmark persistence uses PostgreSQL independently of the runtime routing
service. Database credentials and connection settings therefore belong to the
Benchmark Service rather than ``local_ai_router``.
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkDatabaseSettings:
    """
    PostgreSQL connection settings used by the Benchmark Service.

    Attributes:
        host:
            PostgreSQL hostname or IP address.

        port:
            PostgreSQL TCP port.

        database_name:
            Physical PostgreSQL database containing benchmark persistence.

        username:
            PostgreSQL login role used by the Benchmark Service.

        password:
            Password belonging to the PostgreSQL login role.
    """

    host: str
    port: int
    database_name: str
    username: str
    password: str


def get_benchmark_database_settings() -> BenchmarkDatabaseSettings:
    """
    Load Benchmark Service PostgreSQL settings from environment variables.

    Existing physical database and PostgreSQL role names are deliberately
    preserved during the service-separation refactor. Renaming physical
    database resources is a separate operational concern and is not required
    to establish the application service boundary.

    Returns:
        BenchmarkDatabaseSettings:
            Immutable Benchmark Service database configuration.

    Raises:
        RuntimeError:
            Raised when the required database password is unavailable.
    """

    database_password = os.getenv("LOCAL_AI_BENCHMARK_DB_PASSWORD")

    if not database_password:
        raise RuntimeError("LOCAL_AI_BENCHMARK_DB_PASSWORD environment variable is required.")

    return BenchmarkDatabaseSettings(
        host=os.getenv(
            "LOCAL_AI_BENCHMARK_DB_HOST",
            "127.0.0.1",
        ),
        port=int(
            os.getenv(
                "LOCAL_AI_BENCHMARK_DB_PORT",
                "5432",
            )
        ),
        # Preserve the existing physical database during this refactor.
        database_name=os.getenv(
            "LOCAL_AI_BENCHMARK_DB_NAME",
            "local_ai_router",
        ),
        # Preserve the existing PostgreSQL role for now as well.
        username=os.getenv(
            "LOCAL_AI_BENCHMARK_DB_USER",
            "local_ai_router_app",
        ),
        password=database_password,
    )

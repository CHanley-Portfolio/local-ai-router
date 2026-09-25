"""
Tests for the foundational benchmark persistence configuration.

These tests protect architectural decisions that future SQLAlchemy models and
Alembic migrations will rely upon.
"""

from sqlalchemy import MetaData

from local_ai_router.persistence.benchmark.base import (
    BENCHMARK_SCHEMA_NAME,
    BenchmarkBase,
)


def test_benchmark_base_uses_benchmark_schema() -> None:
    """
    Verify that benchmark ORM tables default to the benchmark PostgreSQL schema.

    This prevents future benchmark models from accidentally being created in
    PostgreSQL's default public schema.
    """

    assert BENCHMARK_SCHEMA_NAME == "benchmark"
    assert BenchmarkBase.metadata.schema == "benchmark"


def test_benchmark_base_uses_sqlalchemy_metadata() -> None:
    """
    Verify that the benchmark declarative base exposes SQLAlchemy metadata.

    Alembic will later use this metadata object to discover benchmark ORM
    tables when generating migrations.
    """

    assert isinstance(BenchmarkBase.metadata, MetaData)


def test_benchmark_constraint_naming_convention_is_configured() -> None:
    """
    Verify that important database constraint types have deterministic names.

    Stable constraint names make future Alembic migrations easier to inspect,
    reproduce, and modify.
    """

    naming_convention = BenchmarkBase.metadata.naming_convention

    assert naming_convention["pk"] == "pk_%(table_name)s"
    assert "fk" in naming_convention
    assert "uq" in naming_convention
    assert "ix" in naming_convention
    assert "ck" in naming_convention

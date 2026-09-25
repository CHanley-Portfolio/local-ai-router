"""
Shared SQLAlchemy declarative base for benchmark models.

Every SQLAlchemy ORM model belonging to the benchamark subsystem will inherit from BenchmarkBase

Keeping a dedicated benchmark base provides two important boundaries:

    1. Benchmark tables default to PostgreSQL's 'benchmark' schema.
    2. Future application tables, such as projects and conversations,
    can use their own metadata and schema without becoming coupled to benchamark persistence.

The naming convention defined here also gives database constraints predictable names.
Predictable names are particularly useful for Alembric migrations because future migrations can refer to
constraints consistently rather than depending on database-generated names.
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

BENCHMARK_SCHEMA_NAME = "benchmark"

BENCHMARK_NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class BenchmarkBase(DeclarativeBase):
    """
    Base class for all benchmark SQLAlchemy ORM models.

    SQLAlchemy collects every table declared by subclasses into this classes 'metadata' object

    Alembic will later inspect 'BenchmarBase.metadata' when generating and applying benchmark database migrations.

    The metadata also sets PostgreSQL's 'benchmark' schema as the default so individual ORM models do not need to repeat the schema name.
    """

    metadata = MetaData(
        schema=BENCHMARK_SCHEMA_NAME,
        naming_convention=BENCHMARK_NAMING_CONVENTION,
    )

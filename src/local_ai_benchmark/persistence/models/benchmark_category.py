"""
SQLAlchemy model for normalized benchmark capability categories.

Categories represent broad evaluation areas such as coding, reasoning,
routing, database work, and project-context use.
"""

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from local_ai_benchmark.persistence.base import BenchmarkBase

if TYPE_CHECKING:
    from local_ai_benchmark.persistence.models.benchmark_case import (
        BenchmarkCase,
    )


class BenchmarkCategory(BenchmarkBase):
    """
    Persist a reusable benchmark category.

    Categories are stored as rows rather than PostgreSQL enum values because
    the benchmark taxonomy is expected to evolve as the router gains new
    capabilities.
    """

    __tablename__ = "benchmark_categories"

    benchmark_category_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    category_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    benchmark_cases: Mapped[list["BenchmarkCase"]] = relationship(
        back_populates="benchmark_category",
    )

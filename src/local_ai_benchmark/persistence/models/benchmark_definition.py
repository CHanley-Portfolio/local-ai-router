"""
SQLAlchemy model describing the source and version of a benchmark.

A benchmark definition identifies where benchmark cases originate.

Examples include:
- Local AI Router
- MMLU-Pro
- GPQA Diamond
- IFEval
- HumanEval+
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from local_ai_benchmark.persistence.base import BenchmarkBase

if TYPE_CHECKING:
    from local_ai_benchmark.persistence.models.benchmark_case import (
        BenchmarkCase,
    )
    from local_ai_benchmark.persistence.models.benchmark_reference_result import (
        BenchmarkReferenceResult,
    )


class BenchmarkDefinition(BenchmarkBase):
    """
    Persist the identity and provenance of a benchmark dataset.

    Benchmark name and version are stored separately so multiple historical
    versions of the same benchmark can coexist without overwriting each other.
    """

    __tablename__ = "benchmark_definitions"

    __table_args__ = (
        UniqueConstraint(
            "benchmark_name",
            "benchmark_version",
            name="uq_benchmark_definitions_name_version",
        ),
    )

    benchmark_definition_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    benchmark_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    benchmark_version: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    source_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    evaluation_harness: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    harness_version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    license_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    benchmark_cases: Mapped[list["BenchmarkCase"]] = relationship(
        back_populates="benchmark_definition",
    )

    benchmark_reference_results: Mapped[list["BenchmarkReferenceResult"]] = relationship(
        back_populates="benchmark_definition",
    )

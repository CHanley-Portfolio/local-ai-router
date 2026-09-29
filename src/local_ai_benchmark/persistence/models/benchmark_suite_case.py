"""
Association model connecting benchmark suites and benchmark cases.

Unlike a simple many-to-many join table, suite membership also stores
execution order and optional weighting information.
"""

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from local_ai_benchmark.persistence.base import BenchmarkBase

if TYPE_CHECKING:
    from local_ai_benchmark.persistence.models.benchmark_case import (
        BenchmarkCase,
    )
    from local_ai_benchmark.persistence.models.benchmark_suite import (
        BenchmarkSuite,
    )


class BenchmarkSuiteCase(BenchmarkBase):
    """
    Associate one benchmark case with one benchmark suite.

    execution_order allows suites to preserve deterministic case ordering.

    weight allows future scoring systems to assign different importance to
    particular cases without duplicating the benchmark case itself.
    """

    __tablename__ = "benchmark_suite_cases"

    benchmark_suite_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "benchmark.benchmark_suites.benchmark_suite_id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    benchmark_case_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "benchmark.benchmark_cases.benchmark_case_id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    execution_order: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    weight: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    benchmark_suite: Mapped["BenchmarkSuite"] = relationship(
        back_populates="benchmark_suite_cases",
    )

    benchmark_case: Mapped["BenchmarkCase"] = relationship(
        back_populates="benchmark_suite_cases",
    )

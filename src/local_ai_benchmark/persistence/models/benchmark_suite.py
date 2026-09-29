"""
SQLAlchemy model describing a versioned collection of benchmark cases.

A suite represents the set of cases selected for one type of benchmark run.

Examples include:
- local_ai_router_v1
- development_standardized_v1
- full_periodic_v1
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from local_ai_benchmark.persistence.base import BenchmarkBase

if TYPE_CHECKING:
    from local_ai_benchmark.persistence.models.benchmark_run import (
        BenchmarkRun,
    )
    from local_ai_benchmark.persistence.models.benchmark_suite_case import (
        BenchmarkSuiteCase,
    )


class BenchmarkSuite(BenchmarkBase):
    """
    Persist a versioned benchmark suite.

    Suite versioning ensures that adding or removing cases later does not make
    historical benchmark runs ambiguous.
    """

    __tablename__ = "benchmark_suites"

    __table_args__ = (
        UniqueConstraint(
            "suite_name",
            "suite_version",
            name="uq_benchmark_suites_name_version",
        ),
    )

    benchmark_suite_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    suite_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    suite_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
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

    benchmark_suite_cases: Mapped[list["BenchmarkSuiteCase"]] = relationship(
        back_populates="benchmark_suite",
    )

    benchmark_runs: Mapped[list["BenchmarkRun"]] = relationship(
        back_populates="benchmark_suite",
    )

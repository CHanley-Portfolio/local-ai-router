"""
SQLAlchemy model representing one execution of a benchmark suite.

A BenchmarkRun records the controlled environment under which a benchmark
suite was executed. It connects the selected benchmark suite, model profile,
hardware, software runtime, and context configuration into one durable
historical record.

Individual benchmark case outputs are stored separately and will later
reference this run.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from local_ai_benchmark.persistence.base import BenchmarkBase

if TYPE_CHECKING:
    from local_ai_benchmark.persistence.models.benchmark_case_result import (
        BenchmarkCaseResult,
    )
    from local_ai_benchmark.persistence.models.benchmark_suite import (
        BenchmarkSuite,
    )
    from local_ai_benchmark.persistence.models.context_profile import (
        ContextProfile,
    )
    from local_ai_benchmark.persistence.models.hardware_profile import (
        HardwareProfile,
    )
    from local_ai_benchmark.persistence.models.model_profile import (
        ModelProfile,
    )
    from local_ai_benchmark.persistence.models.runtime_profile import (
        RuntimeProfile,
    )


class BenchmarkRun(BenchmarkBase):
    """
    Persist one historical execution of a benchmark suite.

    Every execution creates a new row. Existing completed benchmark runs are
    never overwritten when the same suite or model is tested again.

    This append-oriented design allows the Local AI Router to compare model
    performance across time, configuration changes, software versions, and
    hardware environments.
    """

    __tablename__ = "benchmark_runs"

    benchmark_run_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    benchmark_suite_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "benchmark.benchmark_suites.benchmark_suite_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    model_profile_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "benchmark.model_profiles.model_profile_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    hardware_profile_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "benchmark.hardware_profiles.hardware_profile_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    runtime_profile_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "benchmark.runtime_profiles.runtime_profile_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    context_profile_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "benchmark.context_profiles.context_profile_id",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    source_git_commit: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    run_mode: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    benchmark_suite: Mapped["BenchmarkSuite"] = relationship(
        back_populates="benchmark_runs",
    )

    model_profile: Mapped["ModelProfile"] = relationship(
        back_populates="benchmark_runs",
    )

    hardware_profile: Mapped["HardwareProfile"] = relationship(
        back_populates="benchmark_runs",
    )

    runtime_profile: Mapped["RuntimeProfile"] = relationship(
        back_populates="benchmark_runs",
    )

    context_profile: Mapped["ContextProfile | None"] = relationship(
        back_populates="benchmark_runs",
    )

    benchmark_case_results: Mapped[list["BenchmarkCaseResult"]] = relationship(
        back_populates="benchmark_run",
    )

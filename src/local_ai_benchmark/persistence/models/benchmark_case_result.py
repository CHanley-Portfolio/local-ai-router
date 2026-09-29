"""
SQLAlchemy model representing the result of one benchmark case within a run.

A BenchmarkCaseResult preserves the generated output, pass/fail state,
aggregate quality score, diagnostics, and execution lifecycle for one
benchmark case.

Detailed rubric scores and performance telemetry are stored in related tables.
"""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from local_ai_benchmark.persistence.base import BenchmarkBase

if TYPE_CHECKING:
    from local_ai_benchmark.persistence.models.benchmark_case import (
        BenchmarkCase,
    )
    from local_ai_benchmark.persistence.models.benchmark_performance_metric import (
        BenchmarkPerformanceMetric,
    )
    from local_ai_benchmark.persistence.models.benchmark_quality_score import (
        BenchmarkQualityScore,
    )
    from local_ai_benchmark.persistence.models.benchmark_run import (
        BenchmarkRun,
    )


class BenchmarkCaseResult(BenchmarkBase):
    """
    Persist the outcome of one benchmark case during one benchmark run.

    Version 1 permits one result for each run/case combination. If repeated
    trials are introduced later, the schema can add a trial number and expand
    the uniqueness constraint.
    """

    __tablename__ = "benchmark_case_results"

    __table_args__ = (
        UniqueConstraint(
            "benchmark_run_id",
            "benchmark_case_id",
            name="uq_benchmark_case_results_run_case",
        ),
    )

    benchmark_case_result_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    benchmark_run_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "benchmark.benchmark_runs.benchmark_run_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    benchmark_case_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "benchmark.benchmark_cases.benchmark_case_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    result_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    raw_model_response: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    normalized_quality_score: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    passed: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    diagnostic_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    error_type: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    benchmark_run: Mapped["BenchmarkRun"] = relationship(
        back_populates="benchmark_case_results",
    )

    benchmark_case: Mapped["BenchmarkCase"] = relationship(
        back_populates="benchmark_case_results",
    )

    quality_scores: Mapped[list["BenchmarkQualityScore"]] = relationship(
        back_populates="benchmark_case_result",
    )

    performance_metrics: Mapped["BenchmarkPerformanceMetric | None"] = relationship(
        back_populates="benchmark_case_result",
        uselist=False,
    )

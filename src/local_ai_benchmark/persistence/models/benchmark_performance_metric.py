"""
SQLAlchemy model for case-level benchmark performance telemetry.

Quality and performance are deliberately stored separately so model selection
can compare answer quality against latency, throughput, memory use, and token
processing behavior without conflating those measurements.
"""

from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import BigInteger, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from local_ai_benchmark.persistence.base import BenchmarkBase

if TYPE_CHECKING:
    from local_ai_benchmark.persistence.models.benchmark_case_result import (
        BenchmarkCaseResult,
    )


class BenchmarkPerformanceMetric(BenchmarkBase):
    """
    Persist performance telemetry for one benchmark case result.

    The case-result ID serves as both primary key and foreign key, enforcing a
    one-to-zero-or-one relationship between a case result and its performance
    measurement record.
    """

    __tablename__ = "benchmark_performance_metrics"

    benchmark_case_result_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "benchmark.benchmark_case_results.benchmark_case_result_id",
            ondelete="RESTRICT",
        ),
        primary_key=True,
    )

    total_duration_ns: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    time_to_first_token_ns: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    model_load_duration_ns: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    prompt_token_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    prompt_eval_duration_ns: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    prompt_tokens_per_second: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    output_token_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    output_eval_duration_ns: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    output_tokens_per_second: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    baseline_vram_bytes: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    peak_vram_bytes: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    peak_system_ram_bytes: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    backend_metrics: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    benchmark_case_result: Mapped["BenchmarkCaseResult"] = relationship(
        back_populates="performance_metrics",
    )

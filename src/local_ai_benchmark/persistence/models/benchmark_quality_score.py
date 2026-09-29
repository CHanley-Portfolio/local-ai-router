"""
SQLAlchemy model for criterion-level benchmark quality scoring.

Aggregate scores belong to BenchmarkCaseResult, while this table preserves the
individual scoring criteria used to produce that aggregate result.
"""

from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import BigInteger, Boolean, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from local_ai_benchmark.persistence.base import BenchmarkBase

if TYPE_CHECKING:
    from local_ai_benchmark.persistence.models.benchmark_case_result import (
        BenchmarkCaseResult,
    )


class BenchmarkQualityScore(BenchmarkBase):
    """
    Persist one detailed quality criterion for a benchmark case result.

    Examples might include correctness, instruction compliance, architectural
    reasoning, schema validity, or retrieval accuracy.
    """

    __tablename__ = "benchmark_quality_scores"

    benchmark_quality_score_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    benchmark_case_result_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "benchmark.benchmark_case_results.benchmark_case_result_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    criterion_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    raw_score: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    max_score: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    normalized_score: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    passed: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    scorer_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    scorer_version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    details: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    benchmark_case_result: Mapped["BenchmarkCaseResult"] = relationship(
        back_populates="quality_scores",
    )

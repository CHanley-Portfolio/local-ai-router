"""
SQLAlchemy model for externally published benchmark reference results.

Reference results are deliberately stored separately from locally executed
BenchmarkRun data. This prevents vendor-, paper-, or benchmark-published
scores from being mistaken for measurements produced by the Local AI Router.

Each row represents one reported metric for one model variant against one
benchmark definition.
"""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from local_ai_benchmark.persistence.base import BenchmarkBase

if TYPE_CHECKING:
    from local_ai_benchmark.persistence.models.benchmark_definition import (
        BenchmarkDefinition,
    )
    from local_ai_benchmark.persistence.models.model_variant import (
        ModelVariant,
    )


class BenchmarkReferenceResult(BenchmarkBase):
    """
    Persist one externally reported benchmark measurement.

    These records provide comparison points for locally measured model
    performance but are never treated as local benchmark runs.

    Source metadata preserves enough provenance to understand where a score
    came from and how the external evaluation was performed.
    """

    __tablename__ = "benchmark_reference_results"

    benchmark_reference_result_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    benchmark_definition_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "benchmark.benchmark_definitions.benchmark_definition_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    model_variant_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "benchmark.model_variants.model_variant_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    source_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    source_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    source_model_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    metric_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    score_value: Mapped[Decimal] = mapped_column(
        Numeric,
        nullable=False,
    )

    score_unit: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    evaluation_split: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    context_length_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    reported_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    source_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    benchmark_definition: Mapped["BenchmarkDefinition"] = relationship(
        back_populates="benchmark_reference_results",
    )

    model_variant: Mapped["ModelVariant"] = relationship(
        back_populates="benchmark_reference_results",
    )

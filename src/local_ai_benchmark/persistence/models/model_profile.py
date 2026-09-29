"""
SQLAlchemy model representing a benchmark inference configuration.

A ModelProfile describes how a specific model variant should be executed
during a benchmark rather than identifying the artifact itself.
"""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from local_ai_benchmark.persistence.base import BenchmarkBase

if TYPE_CHECKING:
    from local_ai_benchmark.persistence.models.benchmark_run import (
        BenchmarkRun,
    )
    from local_ai_benchmark.persistence.models.model_variant import ModelVariant


class ModelProfile(BenchmarkBase):
    """
    Persist a repeatable inference configuration for a model variant.

    Separating configuration from model identity allows the same model artifact
    to be benchmarked under different generation or reasoning settings without
    pretending those configurations are different models.
    """

    __tablename__ = "model_profiles"

    __table_args__ = (
        UniqueConstraint(
            "model_variant_id",
            "profile_name",
            name="uq_model_profiles_variant_profile_name",
        ),
    )

    model_profile_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    model_variant_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "benchmark.model_variants.model_variant_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    profile_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    temperature: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    top_p: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    seed: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    max_output_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    reasoning_enabled: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    reasoning_effort: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    backend_options: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    model_variant: Mapped["ModelVariant"] = relationship(
        back_populates="model_profiles",
    )

    benchmark_runs: Mapped[list["BenchmarkRun"]] = relationship(
        back_populates="model_profile",
    )

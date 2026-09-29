"""
SQLAlchemy model representing a specific loadable model artifact.

A model variant connects conceptual model identity to an optional quantization
and records backend-specific artifact information such as the model name and digest used by ollama.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from local_ai_benchmark.persistence.base import BenchmarkBase

if TYPE_CHECKING:
    from local_ai_benchmark.persistence.models.benchmark_model import (
        BenchmarkModel,
    )
    from local_ai_benchmark.persistence.models.benchmark_reference_result import (
        BenchmarkReferenceResult,
    )
    from local_ai_benchmark.persistence.models.model_profile import ModelProfile
    from local_ai_benchmark.persistence.models.quantization import Quantization


class ModelVariant(BenchmarkBase):
    """
    Represent one concrete model artifactavailable to an inference backend.

    Different quantizations, versions, or artifact digests of the same conceptual model
    are stored as seperate variants so benchmark results can identify exactly what was tested.
    """

    __tablename__ = "model_variants"

    __table_args__ = (
        UniqueConstraint(
            "backend_model_name",
            "model_digest",
            name="uq_model_variants_backend_name_digest",
        ),
    )

    model_variant_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    model_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "benchmark.models.model_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    quantization_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "benchmark.quantizations.quantization_id",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    model_version: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    backend_model_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    model_digest: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    advertised_context_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    artifact_size_bytes: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    source_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    model: Mapped["BenchmarkModel"] = relationship(
        back_populates="model_variants",
    )

    quantization: Mapped["Quantization | None"] = relationship(
        back_populates="model_variants",
    )

    model_profiles: Mapped[list["ModelProfile"]] = relationship(
        back_populates="model_variant",
    )

    benchmark_reference_results: Mapped[list["BenchmarkReferenceResult"]] = relationship(
        back_populates="model_variant",
    )

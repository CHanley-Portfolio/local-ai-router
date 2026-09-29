"""
SQLAlchemy model representing a conceptual AI model.

A BenchmarkModel represents the underlying model identity, such as "Qwen 3.5 9B".
It deliberately does not represent a particular quantization, download artifact, or inference configuration.

Those concerns belong to ModelVariant and ModelProfile respectively.
"""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from local_ai_benchmark.persistence.base import BenchmarkBase

if TYPE_CHECKING:
    from local_ai_benchmark.persistence.models.model_variant import ModelVariant


class BenchmarkModel(BenchmarkBase):
    """
    Persist the canonical identity of an AI model.

    Examples:
        Qwen 3.5 9B
        Llama 3.1 8B
        DeepSeek model family members

    Model identity is intentionally seperate from model artifactes so several quantizations or
    backend-specific versions can reference one conceptual model.
    """

    __tablename__ = "models"

    __table_args__ = (
        UniqueConstraint(
            "publisher",
            "model_name",
            name="uq_models_publisher_model_name",
        ),
    )

    model_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    model_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    model_family: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    parameter_count_billion: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    publisher: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    license_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    source_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    model_variants: Mapped[list["ModelVariant"]] = relationship(
        back_populates="model",
    )

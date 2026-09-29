"""
SQLAlchemy model for normalizated model quantization definitions.

Quantization is stored independently because the same quantization format may be used by many different model variants.
"""

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from local_ai_benchmark.persistence.base import BenchmarkBase

if TYPE_CHECKING:
    from local_ai_benchmark.persistence.models.model_variant import ModelVariant


class Quantization(BenchmarkBase):
    """
    Describe a reusable model quantization format

    Examples include Q4_K_M, Q8_0 and FP16
    """

    __tablename__ = "quantizations"

    quantization_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    quantization_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    bits_per_weight: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    model_variants: Mapped[list["ModelVariant"]] = relationship(back_populates="quantization")

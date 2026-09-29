"""
SQLAlchemy model describing how model context is configured for a benchmark.

Context configuration is separated from model configuration because the same
model profile may later be tested under direct prompting, retrieval-assisted
context, different context windows, or different retrieval strategies.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from local_ai_benchmark.persistence.base import BenchmarkBase

if TYPE_CHECKING:
    from local_ai_benchmark.persistence.models.benchmark_run import (
        BenchmarkRun,
    )


class ContextProfile(BenchmarkBase):
    """
    Persist the context strategy used for benchmark execution.

    Actual prompt token counts vary by benchmark case and therefore belong to
    case-level performance measurements rather than this configuration table.
    """

    __tablename__ = "context_profiles"

    context_profile_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    profile_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    configured_context_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    context_strategy: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    retrieval_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    retrieval_top_k: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    chunk_size_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    chunk_overlap_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    additional_options: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    benchmark_runs: Mapped[list["BenchmarkRun"]] = relationship(
        back_populates="context_profile",
    )

"""
SQLAlchemy model representing one versioned benchmark task.

A benchmark case contains the exact prompt and evaluation information required
to execute and score one benchmark item.

Historical cases are versioned rather than overwritten so previous benchmark
runs always remain traceable to the definition that produced them.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from local_ai_benchmark.persistence.base import BenchmarkBase

if TYPE_CHECKING:
    from local_ai_benchmark.persistence.models.benchmark_case_result import (
        BenchmarkCaseResult,
    )
    from local_ai_benchmark.persistence.models.benchmark_case_tag import (
        BenchmarkCaseTag,
    )
    from local_ai_benchmark.persistence.models.benchmark_category import (
        BenchmarkCategory,
    )
    from local_ai_benchmark.persistence.models.benchmark_definition import (
        BenchmarkDefinition,
    )
    from local_ai_benchmark.persistence.models.benchmark_suite_case import (
        BenchmarkSuiteCase,
    )


class BenchmarkCase(BenchmarkBase):
    """
    Persist one version of a benchmark prompt or evaluation task.

    The external_case_id is the stable identifier used by the source benchmark
    or by our Local AI Router benchmark dataset.

    Combining benchmark definition, external case ID, and case version prevents
    two distinct versions of the same benchmark task from being confused.
    """

    __tablename__ = "benchmark_cases"

    __table_args__ = (
        UniqueConstraint(
            "benchmark_definition_id",
            "external_case_id",
            "case_version",
            name="uq_benchmark_cases_definition_external_id_version",
        ),
    )

    benchmark_case_id: Mapped[int] = mapped_column(
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

    benchmark_category_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "benchmark.benchmark_categories.benchmark_category_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    external_case_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    case_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    evaluation_target: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    prompt_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    context_fixture: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    scoring_method: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    expected_answer: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    expected_route_mode: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    expected_criteria: Mapped[dict[str, Any] | list[Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    critical: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
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
        back_populates="benchmark_cases",
    )

    benchmark_category: Mapped["BenchmarkCategory"] = relationship(
        back_populates="benchmark_cases",
    )

    benchmark_case_tags: Mapped[list["BenchmarkCaseTag"]] = relationship(
        back_populates="benchmark_case",
    )

    benchmark_suite_cases: Mapped[list["BenchmarkSuiteCase"]] = relationship(
        back_populates="benchmark_case",
    )

    benchmark_case_results: Mapped[list["BenchmarkCaseResult"]] = relationship(
        back_populates="benchmark_case",
    )

"""
Association model connecting benchmark cases and reusable tags.

The composite primary key prevents the same tag from being assigned to the
same benchmark case more than once.
"""

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from local_ai_benchmark.persistence.base import BenchmarkBase

if TYPE_CHECKING:
    from local_ai_benchmark.persistence.models.benchmark_case import (
        BenchmarkCase,
    )
    from local_ai_benchmark.persistence.models.benchmark_tag import (
        BenchmarkTag,
    )


class BenchmarkCaseTag(BenchmarkBase):
    """
    Associate one benchmark case with one benchmark tag.

    This table resolves the many-to-many relationship between cases and tags.
    """

    __tablename__ = "benchmark_case_tags"

    benchmark_case_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "benchmark.benchmark_cases.benchmark_case_id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    benchmark_tag_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "benchmark.benchmark_tags.benchmark_tag_id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    benchmark_case: Mapped["BenchmarkCase"] = relationship(
        back_populates="benchmark_case_tags",
    )

    benchmark_tag: Mapped["BenchmarkTag"] = relationship(
        back_populates="benchmark_case_tags",
    )

"""
SQLAlchemy model for reusable benchmark tags.

Tags provide more detailed classification than a benchmark case's single
primary category.

Examples include:
- python
- fastapi
- retrieval
- async
- long_context
"""

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from local_ai_benchmark.persistence.base import BenchmarkBase

if TYPE_CHECKING:
    from local_ai_benchmark.persistence.models.benchmark_case_tag import (
        BenchmarkCaseTag,
    )


class BenchmarkTag(BenchmarkBase):
    """
    Persist a reusable benchmark tag.

    One tag may be assigned to many benchmark cases through BenchmarkCaseTag.
    """

    __tablename__ = "benchmark_tags"

    benchmark_tag_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    tag_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    benchmark_case_tags: Mapped[list["BenchmarkCaseTag"]] = relationship(
        back_populates="benchmark_tag",
    )

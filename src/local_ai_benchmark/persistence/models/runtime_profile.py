"""
SQLAlchemy model describing the software runtime used for a benchmark.

Runtime information is separated from physical hardware because drivers,
operating systems, Python versions, and inference backends may change without
the machine itself changing.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from local_ai_benchmark.persistence.base import BenchmarkBase

if TYPE_CHECKING:
    from local_ai_benchmark.persistence.models.benchmark_run import (
        BenchmarkRun,
    )


class RuntimeProfile(BenchmarkBase):
    """
    Persist the software environment used during benchmark execution.

    Examples of run-dependent software include the NVIDIA driver, CUDA
    runtime, Python interpreter, and Ollama or another inference backend.
    """

    __tablename__ = "runtime_profiles"

    runtime_profile_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    profile_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    operating_system: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    operating_system_version: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    kernel_version: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    python_version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    nvidia_driver_version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    cuda_version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    backend_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    backend_version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    benchmark_runs: Mapped[list["BenchmarkRun"]] = relationship(
        back_populates="runtime_profile",
    )

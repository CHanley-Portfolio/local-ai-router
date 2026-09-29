"""
SQLAlchemy model describing physical benchmark hardware.

Hardware profiles contain relatively stable physical characteristics such as
CPU, installed RAM, GPU model, GPU count, and VRAM.

Software versions do not belong here because drivers, CUDA, Python, and the
inference backend may change while the physical machine remains the same.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from local_ai_benchmark.persistence.base import BenchmarkBase

if TYPE_CHECKING:
    from local_ai_benchmark.persistence.models.benchmark_run import (
        BenchmarkRun,
    )


class HardwareProfile(BenchmarkBase):
    """
    Persist the physical hardware used for benchmark execution.

    A benchmark run will later reference one hardware profile so historical
    results can be compared only against appropriately compatible machines.
    """

    __tablename__ = "hardware_profiles"

    hardware_profile_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    profile_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    cpu_model: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    system_ram_bytes: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    gpu_model: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    gpu_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    vram_per_gpu_bytes: Mapped[int | None] = mapped_column(
        BigInteger,
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

    benchmark_runs: Mapped[list["BenchmarkRun"]] = relationship(
        back_populates="hardware_profile",
    )

"""
PostgreSQL integration tests for benchmark persistence.

These tests exercise the real PostgreSQL schema rather than SQLAlchemy
metadata alone.

They are intentionally restricted to the ``local_ai_router_test`` database.
All benchmark runs and result rows created by a test are wrapped in a
transaction and rolled back afterward so repeated test execution does not
pollute benchmark history.
"""

import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Generator

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from local_ai_benchmark.config import get_benchmark_database_settings
from local_ai_benchmark.persistence.database import create_database_engine
from local_ai_benchmark.persistence.models import (
    BenchmarkCaseResult,
    BenchmarkPerformanceMetric,
    BenchmarkQualityScore,
    BenchmarkRun,
)
from local_ai_benchmark.persistence.seeding import (
    seed_benchmark_test_data,
)


@pytest.fixture
def benchmark_database_session() -> Generator[Session, None, None]:
    """
    Provide a transaction-isolated PostgreSQL integration-test session.

    The fixture skips automatically when database credentials are unavailable
    or when the configured database is not ``local_ai_router_test``.

    This keeps the normal unit-test suite safe on machines and CI jobs that do
    not currently provide PostgreSQL integration infrastructure.

    Every database change made through this session is rolled back when the
    test finishes.
    """

    if not os.getenv("LOCAL_AI_BENCHMARK_DB_PASSWORD"):
        pytest.skip("PostgreSQL integration test requires LOCAL_AI_BENCHMARK_DB_PASSWORD.")

    database_settings = get_benchmark_database_settings()

    if database_settings.database_name != "local_ai_router_test":
        pytest.skip(
            "PostgreSQL benchmark integration tests may only run against local_ai_router_test."
        )

    database_engine = create_database_engine(database_settings)

    try:
        with database_engine.connect() as database_connection:
            database_transaction = database_connection.begin()

            try:
                with Session(
                    bind=database_connection,
                    autoflush=False,
                    expire_on_commit=False,
                ) as database_session:
                    yield database_session
            finally:
                database_transaction.rollback()
    finally:
        database_engine.dispose()


def test_multiple_benchmark_runs_are_preserved_and_queryable(
    benchmark_database_session: Session,
) -> None:
    """
    Verify repeated benchmark executions remain separate historical records.

    Two runs use exactly the same suite, model profile, hardware, runtime, and
    benchmark case. Their result quality and performance values differ.

    Querying the history must return both runs independently rather than one
    execution overwriting the other.
    """

    seed_ids = seed_benchmark_test_data(benchmark_database_session)

    first_started_at = datetime(
        2026,
        1,
        1,
        12,
        0,
        tzinfo=timezone.utc,
    )
    second_started_at = first_started_at + timedelta(minutes=10)

    first_run = BenchmarkRun(
        benchmark_suite_id=seed_ids.benchmark_suite_id,
        model_profile_id=seed_ids.model_profile_id,
        hardware_profile_id=seed_ids.hardware_profile_id,
        runtime_profile_id=seed_ids.runtime_profile_id,
        context_profile_id=seed_ids.context_profile_id,
        source_git_commit="integration-test-first",
        run_mode="integration_test",
        status="completed",
        started_at=first_started_at,
        completed_at=first_started_at + timedelta(seconds=5),
        notes="First synthetic historical benchmark run.",
    )

    second_run = BenchmarkRun(
        benchmark_suite_id=seed_ids.benchmark_suite_id,
        model_profile_id=seed_ids.model_profile_id,
        hardware_profile_id=seed_ids.hardware_profile_id,
        runtime_profile_id=seed_ids.runtime_profile_id,
        context_profile_id=seed_ids.context_profile_id,
        source_git_commit="integration-test-second",
        run_mode="integration_test",
        status="completed",
        started_at=second_started_at,
        completed_at=second_started_at + timedelta(seconds=4),
        notes="Second synthetic historical benchmark run.",
    )

    benchmark_database_session.add_all(
        [
            first_run,
            second_run,
        ]
    )
    benchmark_database_session.flush()

    first_result = BenchmarkCaseResult(
        benchmark_run_id=first_run.benchmark_run_id,
        benchmark_case_id=seed_ids.benchmark_case_id,
        result_status="completed",
        raw_model_response="ready",
        normalized_quality_score=Decimal("80"),
        passed=True,
    )

    second_result = BenchmarkCaseResult(
        benchmark_run_id=second_run.benchmark_run_id,
        benchmark_case_id=seed_ids.benchmark_case_id,
        result_status="completed",
        raw_model_response="ready",
        normalized_quality_score=Decimal("95"),
        passed=True,
    )

    benchmark_database_session.add_all(
        [
            first_result,
            second_result,
        ]
    )
    benchmark_database_session.flush()

    benchmark_database_session.add_all(
        [
            BenchmarkQualityScore(
                benchmark_case_result_id=(first_result.benchmark_case_result_id),
                criterion_name="correctness",
                raw_score=Decimal("3.2"),
                max_score=Decimal("4"),
                normalized_score=Decimal("80"),
                passed=True,
                scorer_type="integration_test",
            ),
            BenchmarkQualityScore(
                benchmark_case_result_id=(second_result.benchmark_case_result_id),
                criterion_name="correctness",
                raw_score=Decimal("3.8"),
                max_score=Decimal("4"),
                normalized_score=Decimal("95"),
                passed=True,
                scorer_type="integration_test",
            ),
            BenchmarkPerformanceMetric(
                benchmark_case_result_id=(first_result.benchmark_case_result_id),
                total_duration_ns=5_000_000_000,
                output_token_count=20,
                peak_vram_bytes=8_000_000_000,
            ),
            BenchmarkPerformanceMetric(
                benchmark_case_result_id=(second_result.benchmark_case_result_id),
                total_duration_ns=4_000_000_000,
                output_token_count=20,
                peak_vram_bytes=7_500_000_000,
            ),
        ]
    )

    benchmark_database_session.flush()

    historical_rows = benchmark_database_session.execute(
        select(
            BenchmarkRun.benchmark_run_id,
            BenchmarkRun.started_at,
            BenchmarkCaseResult.normalized_quality_score,
            BenchmarkPerformanceMetric.total_duration_ns,
            BenchmarkPerformanceMetric.peak_vram_bytes,
        )
        .join(
            BenchmarkCaseResult,
            BenchmarkCaseResult.benchmark_run_id == BenchmarkRun.benchmark_run_id,
        )
        .join(
            BenchmarkPerformanceMetric,
            BenchmarkPerformanceMetric.benchmark_case_result_id
            == BenchmarkCaseResult.benchmark_case_result_id,
        )
        .where(
            BenchmarkRun.benchmark_run_id.in_(
                [
                    first_run.benchmark_run_id,
                    second_run.benchmark_run_id,
                ]
            )
        )
        .order_by(BenchmarkRun.started_at)
    ).all()

    assert len(historical_rows) == 2

    first_history_row = historical_rows[0]
    second_history_row = historical_rows[1]

    assert first_history_row.benchmark_run_id == first_run.benchmark_run_id
    assert second_history_row.benchmark_run_id == second_run.benchmark_run_id

    assert first_history_row.normalized_quality_score == Decimal("80")
    assert second_history_row.normalized_quality_score == Decimal("95")

    assert first_history_row.total_duration_ns == 5_000_000_000
    assert second_history_row.total_duration_ns == 4_000_000_000

    assert first_history_row.peak_vram_bytes == 8_000_000_000
    assert second_history_row.peak_vram_bytes == 7_500_000_000

    # Both rows reference the same benchmark configuration. The differing
    # run IDs prove repeated executions are stored as separate history.
    assert first_run.benchmark_suite_id == second_run.benchmark_suite_id
    assert first_run.model_profile_id == second_run.model_profile_id
    assert first_run.hardware_profile_id == second_run.hardware_profile_id
    assert first_run.runtime_profile_id == second_run.runtime_profile_id

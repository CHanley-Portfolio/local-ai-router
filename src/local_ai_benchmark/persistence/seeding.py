"""
Idempotent seed support for benchmark integration testing.

The seed data created here is deliberately synthetic.
It exists only to give database integration tests a stable set of related benchmark configuration records without polluting real benchmark history.

The public seeding function accepts an existing SQLAlchemy Session so tests and future tooling can control transactio boundaries themselves.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from local_ai_benchmark.config import get_benchmark_database_settings
from local_ai_benchmark.persistence.database import (
    create_database_engine,
    create_database_session_factory,
)
from local_ai_benchmark.persistence.models import (
    BenchmarkCase,
    BenchmarkCategory,
    BenchmarkDefinition,
    BenchmarkModel,
    BenchmarkSuite,
    BenchmarkSuiteCase,
    ContextProfile,
    HardwareProfile,
    ModelProfile,
    ModelVariant,
    Quantization,
    RuntimeProfile,
)


@dataclass(frozen=True)
class BenchmarkSeedIds:
    """
    Return the database identifiers created or reused by test seeding.

    Returning the IDs gives integration tests stable references
    without requiring them  to repeat lookup logic.
    """

    model_id: int
    quantization_id: int
    model_variant_id: int
    model_profile_id: int
    benchmark_definition_id: int
    benchmark_category_id: int
    benchmark_case_id: int
    benchmark_suite_id: int
    hardware_profile_id: int
    runtime_profile_id: int
    context_profile_id: int


def _get_or_create(
    database_session: Session,
    model_type: type[Any],
    lookup_values: dict[str, Any],
    create_values: dict[str, Any] | None = None,
) -> Any:
    """
    Find one ORM row by deterministic lookup values or create it.

    Args:
        database_session:
            Active SQLAlchemy session controlling the transaction.

        model_type:
            ORM model class to query and potentially instantiate.

        lookup_values:
            Column/value paris that identify teh seed record.

        create_values:
            Additional values required only when a new row must be created.

    Returns:
        Any:
            Existing or newly created ORM instance.

    Notes:
        The function calls 'flush()' after insertion so generated primary keys
        are immediately available to dependant seed records.

        It deliberately does not commit. Transaction ownership remains with the caller.
    """

    filter_expressions = [
        getattr(model_type, column_name) == column_value
        for column_name, column_value in lookup_values.items()
    ]

    existing_record = database_session.scalar(select(model_type).where(*filter_expressions))

    if existing_record is not None:
        return existing_record

    record_values = dict(lookup_values)

    if create_values is not None:
        record_values.update(create_values)

    new_record = model_type(**record_values)

    database_session.add(new_record)
    database_session.flush()

    return new_record


def seed_benchmark_test_data(database_session: Session) -> BenchmarkSeedIds:
    """
    Seed the minimum related benchmark data required by integration tests.

    The operation is idempotent. Running it repeatedly against the
    same test database reuses the existing seed records instead of creating duplicates.

    Args:
        database_session:
            SQLAlchemy session connected to the benchamark test database.

    Returns:
        BenchmarkSeedIds:
            Primary-key identifiers for the seeded configuration records.
    """

    benchmark_model = _get_or_create(
        database_session,
        BenchmarkModel,
        {
            "publisher": "local_ai_router_test",
            "model_name": "seed_test_model",
        },
        {
            "model_family": "seed_test_family",
            "parameter_count_billion": Decimal("1.0"),
            "notes": "Synthetic model used only for database integration tests.",
        },
    )

    quantization = _get_or_create(
        database_session,
        Quantization,
        {
            "quantization_name": "seed_q4",
        },
        {
            "bits_per_weight": Decimal("4"),
            "description": "Synthetic quantization used by integration tests.",
        },
    )

    model_variant = _get_or_create(
        database_session,
        ModelVariant,
        {
            "backend_model_name": "seed_test_model:q4",
            "model_digest": "seed-test-model-digest-v1",
        },
        {
            "model_id": benchmark_model.model_id,
            "quantization_id": quantization.quantization_id,
            "model_version": "1.0",
            "advertised_context_tokens": 8192,
        },
    )

    model_profile = _get_or_create(
        database_session,
        ModelProfile,
        {
            "model_variant_id": model_variant.model_variant_id,
            "profile_name": "seed_default",
        },
        {
            "temperature": Decimal("0"),
            "top_p": Decimal("1"),
            "seed": 1,
            "max_output_tokens": 256,
            "reasoning_enabled": False,
        },
    )

    benchmark_definition = _get_or_create(
        database_session,
        BenchmarkDefinition,
        {
            "benchmark_name": "local_ai_router_seed",
            "benchmark_version": "1",
        },
        {
            "evaluation_harness": "local_ai_router",
            "description": (
                "Synthetic benchmark definition used only for database integration testing."
            ),
        },
    )

    benchmark_category = _get_or_create(
        database_session,
        BenchmarkCategory,
        {
            "category_name": "seed_validation",
        },
        {
            "description": "Synthetic integration-test benchmark category.",
        },
    )

    benchmark_case = _get_or_create(
        database_session,
        BenchmarkCase,
        {
            "benchmark_definition_id": (benchmark_definition.benchmark_definition_id),
            "external_case_id": "seed.case.001",
            "case_version": 1,
        },
        {
            "benchmark_category_id": (benchmark_category.benchmark_category_id),
            "evaluation_target": "model",
            "prompt_text": "Return exactly the word ready.",
            "scoring_method": "exact_match",
            "expected_answer": "ready",
            "critical": False,
        },
    )

    benchmark_suite = _get_or_create(
        database_session,
        BenchmarkSuite,
        {
            "suite_name": "local_ai_router_seed",
            "suite_version": 1,
        },
        {
            "description": "Synthetic integration-test benchmark suite.",
        },
    )

    _get_or_create(
        database_session,
        BenchmarkSuiteCase,
        {
            "benchmark_suite_id": benchmark_suite.benchmark_suite_id,
            "benchmark_case_id": benchmark_case.benchmark_case_id,
        },
        {
            "execution_order": 1,
            "weight": Decimal("1"),
        },
    )

    hardware_profile = _get_or_create(
        database_session,
        HardwareProfile,
        {
            "profile_name": "seed_test_hardware",
        },
        {
            "cpu_model": "Synthetic Test CPU",
            "system_ram_bytes": 17_179_869_184,
            "gpu_model": "Synthetic Test GPU",
            "gpu_count": 1,
            "vram_per_gpu_bytes": 8_589_934_592,
            "notes": "Synthetic hardware. Not a measured physical system.",
        },
    )

    runtime_profile = _get_or_create(
        database_session,
        RuntimeProfile,
        {
            "profile_name": "seed_test_runtime",
            "backend_name": "seed_backend",
            "backend_version": "1.0",
        },
        {
            "operating_system": "Synthetic Test OS",
            "python_version": "3.12",
        },
    )

    context_profile = _get_or_create(
        database_session,
        ContextProfile,
        {
            "profile_name": "seed_direct_context",
            "context_strategy": "direct",
            "configured_context_tokens": 8192,
        },
        {
            "retrieval_enabled": False,
        },
    )

    return BenchmarkSeedIds(
        model_id=benchmark_model.model_id,
        quantization_id=quantization.quantization_id,
        model_variant_id=model_variant.model_variant_id,
        model_profile_id=model_profile.model_profile_id,
        benchmark_definition_id=(benchmark_definition.benchmark_definition_id),
        benchmark_category_id=benchmark_category.benchmark_category_id,
        benchmark_case_id=benchmark_case.benchmark_case_id,
        benchmark_suite_id=benchmark_suite.benchmark_suite_id,
        hardware_profile_id=hardware_profile.hardware_profile_id,
        runtime_profile_id=runtime_profile.runtime_profile_id,
        context_profile_id=context_profile.context_profile_id,
    )


def seed_benchmark_test_database() -> BenchmarkSeedIds:
    """
    Seed the configured test database and commit the transaction.

    This convenience entry point refuses to run against any database other than 'local_ai_router_test'.
    That guard prevents synthetic benchmark records from being accidentally inserted into the development database.

    Returns:
        BenchmarkSeedIds:
            Identifiers of the seeded test records.

    Raises:
        RuntimeError:
            If the configured database is not 'local_ai_router_test'.
    """

    database_settings = get_benchmark_database_settings()

    if database_settings.database_name != "local_ai_router_test":
        raise RuntimeError("Benchmark test seed may only run against 'local_ai_router_test'.")

    database_engine = create_database_engine(database_settings)
    database_session_factory = create_database_session_factory(database_engine)

    try:
        with database_session_factory() as database_session:
            seed_ids = seed_benchmark_test_data(database_session)
            database_session.commit()

            return seed_ids
    finally:
        database_engine.dispose()


if __name__ == "__main__":
    seeded_ids = seed_benchmark_test_database()

    print("Benchmark test seed completed successfully.")
    print(seeded_ids)

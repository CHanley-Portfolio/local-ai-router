"""
Structural tests for the first benchmark persistence ORM models.

These tests validate SQLAlchemy metadata without requiring a live PostgreSQL
database. Database migration and integration behavior will be tested
separately.
"""

from sqlalchemy.orm import configure_mappers

from local_ai_router.persistence.benchmark.base import BenchmarkBase
from local_ai_router.persistence.benchmark.models import (
    BenchmarkCase,
    BenchmarkCaseResult,
    BenchmarkCaseTag,
    BenchmarkDefinition,
    BenchmarkModel,
    BenchmarkPerformanceMetric,
    BenchmarkQualityScore,
    BenchmarkReferenceResult,
    BenchmarkRun,
    BenchmarkSuite,
    BenchmarkSuiteCase,
    ContextProfile,
    HardwareProfile,
    ModelProfile,
    ModelVariant,
    Quantization,
    RuntimeProfile,
)


def test_model_catalog_tables_are_registered() -> None:
    """
    Verify the first model-catalog tables are registered with benchmark metadata.
    """

    expected_table_names = {
        "benchmark.models",
        "benchmark.quantizations",
        "benchmark.model_variants",
        "benchmark.model_profiles",
    }

    assert expected_table_names.issubset(BenchmarkBase.metadata.tables)


def test_model_catalog_tables_use_benchmark_schema() -> None:
    """
    Verify every model-catalog table belongs to the benchmark schema.
    """

    model_catalog_tables = (
        BenchmarkModel.__table__,
        Quantization.__table__,
        ModelVariant.__table__,
        ModelProfile.__table__,
    )

    for database_table in model_catalog_tables:
        assert database_table.schema == "benchmark"


def test_model_variant_foreign_keys_target_expected_tables() -> None:
    """
    Verify model variants reference models and quantizations correctly.
    """

    model_foreign_key = next(iter(ModelVariant.__table__.c.model_id.foreign_keys))
    quantization_foreign_key = next(iter(ModelVariant.__table__.c.quantization_id.foreign_keys))

    assert model_foreign_key.target_fullname == "benchmark.models.model_id"
    assert quantization_foreign_key.target_fullname == "benchmark.quantizations.quantization_id"


def test_model_profile_references_model_variant() -> None:
    """
    Verify model profiles belong to one specific model variant.
    """

    model_variant_foreign_key = next(iter(ModelProfile.__table__.c.model_variant_id.foreign_keys))

    assert model_variant_foreign_key.target_fullname == "benchmark.model_variants.model_variant_id"


def test_quantization_is_optional_for_model_variant() -> None:
    """
    Verify unquantized or otherwise unspecified variants remain representable.
    """

    assert ModelVariant.__table__.c.quantization_id.nullable is True


def test_required_model_catalog_fields_are_not_nullable() -> None:
    """
    Protect required identity fields from accidentally becoming optional.
    """

    assert BenchmarkModel.__table__.c.model_name.nullable is False
    assert BenchmarkModel.__table__.c.publisher.nullable is False

    assert Quantization.__table__.c.quantization_name.nullable is False

    assert ModelVariant.__table__.c.model_id.nullable is False
    assert ModelVariant.__table__.c.backend_model_name.nullable is False

    assert ModelProfile.__table__.c.model_variant_id.nullable is False
    assert ModelProfile.__table__.c.profile_name.nullable is False


def test_benchmark_definition_tables_are_registered() -> None:
    """
    Verify benchmark definition, category, and case tables are registered.
    """

    expected_table_names = {
        "benchmark.benchmark_definitions",
        "benchmark.benchmark_categories",
        "benchmark.benchmark_cases",
    }

    assert expected_table_names.issubset(BenchmarkBase.metadata.tables)


def test_benchmark_case_foreign_keys_target_definition_and_category() -> None:
    """
    Verify every benchmark case references its definition and primary category.
    """

    definition_foreign_key = next(
        iter(BenchmarkCase.__table__.c.benchmark_definition_id.foreign_keys)
    )

    category_foreign_key = next(iter(BenchmarkCase.__table__.c.benchmark_category_id.foreign_keys))

    assert (
        definition_foreign_key.target_fullname
        == "benchmark.benchmark_definitions.benchmark_definition_id"
    )

    assert (
        category_foreign_key.target_fullname
        == "benchmark.benchmark_categories.benchmark_category_id"
    )


def test_benchmark_case_identity_fields_are_required() -> None:
    """
    Verify benchmark cases cannot exist without their core identity fields.
    """

    assert BenchmarkCase.__table__.c.benchmark_definition_id.nullable is False
    assert BenchmarkCase.__table__.c.benchmark_category_id.nullable is False
    assert BenchmarkCase.__table__.c.external_case_id.nullable is False
    assert BenchmarkCase.__table__.c.case_version.nullable is False
    assert BenchmarkCase.__table__.c.evaluation_target.nullable is False
    assert BenchmarkCase.__table__.c.prompt_text.nullable is False
    assert BenchmarkCase.__table__.c.scoring_method.nullable is False
    assert BenchmarkCase.__table__.c.critical.nullable is False


def test_benchmark_case_flexible_metadata_uses_jsonb() -> None:
    """
    Verify variable benchmark metadata uses PostgreSQL JSONB.
    """

    expected_criteria_type = BenchmarkCase.__table__.c.expected_criteria.type
    source_metadata_type = BenchmarkCase.__table__.c.source_metadata.type

    assert expected_criteria_type.__class__.__name__ == "JSONB"
    assert source_metadata_type.__class__.__name__ == "JSONB"


def test_benchmark_definition_name_and_version_form_unique_identity() -> None:
    """
    Verify benchmark definitions protect benchmark/version uniqueness.
    """

    unique_constraints = {
        constraint.name
        for constraint in BenchmarkDefinition.__table__.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    }

    assert "uq_benchmark_definitions_name_version" in unique_constraints


def test_benchmark_tag_and_suite_tables_are_registered() -> None:
    """
    Verify tag, suite, and association tables are registered.
    """

    expected_table_names = {
        "benchmark.benchmark_tags",
        "benchmark.benchmark_case_tags",
        "benchmark.benchmark_suites",
        "benchmark.benchmark_suite_cases",
    }

    assert expected_table_names.issubset(BenchmarkBase.metadata.tables)


def test_benchmark_case_tag_uses_composite_primary_key() -> None:
    """
    Verify one case/tag combination can appear only once.
    """

    primary_key_columns = {column.name for column in BenchmarkCaseTag.__table__.primary_key.columns}

    assert primary_key_columns == {
        "benchmark_case_id",
        "benchmark_tag_id",
    }


def test_benchmark_case_tag_foreign_keys_are_correct() -> None:
    """
    Verify case-tag associations reference the expected parent tables.
    """

    case_foreign_key = next(iter(BenchmarkCaseTag.__table__.c.benchmark_case_id.foreign_keys))
    tag_foreign_key = next(iter(BenchmarkCaseTag.__table__.c.benchmark_tag_id.foreign_keys))

    assert case_foreign_key.target_fullname == "benchmark.benchmark_cases.benchmark_case_id"
    assert tag_foreign_key.target_fullname == "benchmark.benchmark_tags.benchmark_tag_id"


def test_benchmark_suite_name_and_version_form_unique_identity() -> None:
    """
    Verify suite versions cannot be accidentally duplicated.
    """

    unique_constraints = {
        constraint.name
        for constraint in BenchmarkSuite.__table__.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    }

    assert "uq_benchmark_suites_name_version" in unique_constraints


def test_benchmark_suite_case_uses_composite_primary_key() -> None:
    """
    Verify a case can appear only once within one suite.
    """

    primary_key_columns = {
        column.name for column in BenchmarkSuiteCase.__table__.primary_key.columns
    }

    assert primary_key_columns == {
        "benchmark_suite_id",
        "benchmark_case_id",
    }


def test_benchmark_suite_case_foreign_keys_are_correct() -> None:
    """
    Verify suite membership references both suite and case tables.
    """

    suite_foreign_key = next(iter(BenchmarkSuiteCase.__table__.c.benchmark_suite_id.foreign_keys))
    case_foreign_key = next(iter(BenchmarkSuiteCase.__table__.c.benchmark_case_id.foreign_keys))

    assert suite_foreign_key.target_fullname == "benchmark.benchmark_suites.benchmark_suite_id"
    assert case_foreign_key.target_fullname == "benchmark.benchmark_cases.benchmark_case_id"


def test_suite_case_execution_order_and_weight_are_optional() -> None:
    """
    Verify basic suite membership does not require ordering or weighting.
    """

    assert BenchmarkSuiteCase.__table__.c.execution_order.nullable is True
    assert BenchmarkSuiteCase.__table__.c.weight.nullable is True


def test_environment_profile_tables_are_registered() -> None:
    """
    Verify hardware, runtime, and context profile tables are registered.
    """

    expected_table_names = {
        "benchmark.hardware_profiles",
        "benchmark.runtime_profiles",
        "benchmark.context_profiles",
    }

    assert expected_table_names.issubset(BenchmarkBase.metadata.tables)


def test_environment_profile_tables_use_benchmark_schema() -> None:
    """
    Verify environment profile tables remain inside the benchmark schema.
    """

    environment_profile_tables = (
        HardwareProfile.__table__,
        RuntimeProfile.__table__,
        ContextProfile.__table__,
    )

    for database_table in environment_profile_tables:
        assert database_table.schema == "benchmark"


def test_hardware_profile_name_is_unique() -> None:
    """
    Verify hardware profile names uniquely identify known physical profiles.
    """

    unique_constraints = {
        constraint.name
        for constraint in HardwareProfile.__table__.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    }

    assert "uq_hardware_profiles_profile_name" in unique_constraints


def test_hardware_and_runtime_required_fields_are_not_nullable() -> None:
    """
    Verify environment records require their essential identifying fields.
    """

    assert HardwareProfile.__table__.c.profile_name.nullable is False
    assert HardwareProfile.__table__.c.gpu_count.nullable is False

    assert RuntimeProfile.__table__.c.profile_name.nullable is False
    assert RuntimeProfile.__table__.c.backend_name.nullable is False


def test_context_profile_requires_strategy_and_retrieval_state() -> None:
    """
    Verify context profiles explicitly describe their context behavior.
    """

    assert ContextProfile.__table__.c.profile_name.nullable is False
    assert ContextProfile.__table__.c.context_strategy.nullable is False
    assert ContextProfile.__table__.c.retrieval_enabled.nullable is False


def test_context_profile_additional_options_uses_jsonb() -> None:
    """
    Verify backend- or strategy-specific context options use PostgreSQL JSONB.
    """

    additional_options_type = ContextProfile.__table__.c.additional_options.type

    assert additional_options_type.__class__.__name__ == "JSONB"


def test_benchmark_run_table_is_registered() -> None:
    """
    Verify the central benchmark execution table is registered.
    """

    assert "benchmark.benchmark_runs" in BenchmarkBase.metadata.tables


def test_benchmark_run_required_foreign_keys_are_not_nullable() -> None:
    """
    Verify a benchmark run records the required execution environment.
    """

    assert BenchmarkRun.__table__.c.benchmark_suite_id.nullable is False
    assert BenchmarkRun.__table__.c.model_profile_id.nullable is False
    assert BenchmarkRun.__table__.c.hardware_profile_id.nullable is False
    assert BenchmarkRun.__table__.c.runtime_profile_id.nullable is False


def test_benchmark_run_context_profile_is_optional() -> None:
    """
    Verify benchmarks can execute without a dedicated context profile.
    """

    assert BenchmarkRun.__table__.c.context_profile_id.nullable is True


def test_benchmark_run_foreign_keys_target_expected_tables() -> None:
    """
    Verify benchmark runs connect to every expected configuration table.
    """

    expected_foreign_key_targets = {
        "benchmark.benchmark_suites.benchmark_suite_id",
        "benchmark.model_profiles.model_profile_id",
        "benchmark.hardware_profiles.hardware_profile_id",
        "benchmark.runtime_profiles.runtime_profile_id",
        "benchmark.context_profiles.context_profile_id",
    }

    actual_foreign_key_targets = {
        foreign_key.target_fullname for foreign_key in BenchmarkRun.__table__.foreign_keys
    }

    assert actual_foreign_key_targets == expected_foreign_key_targets


def test_benchmark_run_foreign_keys_restrict_parent_deletion() -> None:
    """
    Verify historical runs protect referenced configuration records.

    Deleting a model, hardware, runtime, suite, or context profile that is
    referenced by historical results would damage benchmark provenance.
    """

    for foreign_key in BenchmarkRun.__table__.foreign_keys:
        assert foreign_key.ondelete == "RESTRICT"


def test_benchmark_run_lifecycle_fields_have_expected_nullability() -> None:
    """
    Verify run lifecycle fields can represent active and completed executions.
    """

    assert BenchmarkRun.__table__.c.run_mode.nullable is False
    assert BenchmarkRun.__table__.c.status.nullable is False
    assert BenchmarkRun.__table__.c.started_at.nullable is False
    assert BenchmarkRun.__table__.c.completed_at.nullable is True


def test_benchmark_result_tables_are_registered() -> None:
    """
    Verify case-result, quality-score, and performance tables are registered.
    """

    expected_table_names = {
        "benchmark.benchmark_case_results",
        "benchmark.benchmark_quality_scores",
        "benchmark.benchmark_performance_metrics",
    }

    assert expected_table_names.issubset(BenchmarkBase.metadata.tables)


def test_benchmark_case_result_references_run_and_case() -> None:
    """
    Verify every case result belongs to one run and one benchmark case.
    """

    expected_foreign_key_targets = {
        "benchmark.benchmark_runs.benchmark_run_id",
        "benchmark.benchmark_cases.benchmark_case_id",
    }

    actual_foreign_key_targets = {
        foreign_key.target_fullname for foreign_key in BenchmarkCaseResult.__table__.foreign_keys
    }

    assert actual_foreign_key_targets == expected_foreign_key_targets


def test_benchmark_case_result_run_case_pair_is_unique() -> None:
    """
    Verify version 1 stores at most one result for each run/case pair.
    """

    unique_constraints = {
        constraint.name
        for constraint in BenchmarkCaseResult.__table__.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    }

    assert "uq_benchmark_case_results_run_case" in unique_constraints


def test_benchmark_case_result_required_fields_are_not_nullable() -> None:
    """
    Verify case results require their identity and execution status.
    """

    assert BenchmarkCaseResult.__table__.c.benchmark_run_id.nullable is False
    assert BenchmarkCaseResult.__table__.c.benchmark_case_id.nullable is False
    assert BenchmarkCaseResult.__table__.c.result_status.nullable is False


def test_benchmark_quality_score_references_case_result() -> None:
    """
    Verify detailed quality scores belong to a benchmark case result.
    """

    foreign_key = next(
        iter(BenchmarkQualityScore.__table__.c.benchmark_case_result_id.foreign_keys)
    )

    assert (
        foreign_key.target_fullname == "benchmark.benchmark_case_results.benchmark_case_result_id"
    )


def test_performance_metric_uses_case_result_as_primary_and_foreign_key() -> None:
    """
    Verify performance telemetry is one-to-zero-or-one with a case result.
    """

    primary_key_columns = {
        column.name for column in BenchmarkPerformanceMetric.__table__.primary_key.columns
    }

    assert primary_key_columns == {"benchmark_case_result_id"}

    foreign_key = next(
        iter(BenchmarkPerformanceMetric.__table__.c.benchmark_case_result_id.foreign_keys)
    )

    assert (
        foreign_key.target_fullname == "benchmark.benchmark_case_results.benchmark_case_result_id"
    )


def test_result_flexible_metadata_uses_jsonb() -> None:
    """
    Verify scorer and backend-specific metadata use PostgreSQL JSONB.
    """

    quality_details_type = BenchmarkQualityScore.__table__.c.details.type
    backend_metrics_type = BenchmarkPerformanceMetric.__table__.c.backend_metrics.type

    assert quality_details_type.__class__.__name__ == "JSONB"
    assert backend_metrics_type.__class__.__name__ == "JSONB"


def test_historical_result_foreign_keys_restrict_parent_deletion() -> None:
    """
    Verify benchmark evidence cannot disappear through parent deletion.
    """

    historical_tables = (
        BenchmarkCaseResult.__table__,
        BenchmarkQualityScore.__table__,
        BenchmarkPerformanceMetric.__table__,
    )

    for database_table in historical_tables:
        for foreign_key in database_table.foreign_keys:
            assert foreign_key.ondelete == "RESTRICT"


def test_benchmark_reference_result_table_is_registered() -> None:
    """
    Verify externally published benchmark results have dedicated storage.
    """

    assert "benchmark.benchmark_reference_results" in BenchmarkBase.metadata.tables


def test_benchmark_reference_result_foreign_keys_are_correct() -> None:
    """
    Verify external results identify both benchmark and model variant.
    """

    expected_foreign_key_targets = {
        "benchmark.benchmark_definitions.benchmark_definition_id",
        "benchmark.model_variants.model_variant_id",
    }

    actual_foreign_key_targets = {
        foreign_key.target_fullname
        for foreign_key in BenchmarkReferenceResult.__table__.foreign_keys
    }

    assert actual_foreign_key_targets == expected_foreign_key_targets


def test_benchmark_reference_result_requires_provenance_and_score() -> None:
    """
    Verify an external score cannot exist without basic provenance.
    """

    assert BenchmarkReferenceResult.__table__.c.benchmark_definition_id.nullable is False
    assert BenchmarkReferenceResult.__table__.c.model_variant_id.nullable is False
    assert BenchmarkReferenceResult.__table__.c.source_name.nullable is False
    assert BenchmarkReferenceResult.__table__.c.metric_name.nullable is False
    assert BenchmarkReferenceResult.__table__.c.score_value.nullable is False


def test_benchmark_reference_result_metadata_uses_jsonb() -> None:
    """
    Verify source-specific external benchmark metadata uses PostgreSQL JSONB.
    """

    source_metadata_type = BenchmarkReferenceResult.__table__.c.source_metadata.type

    assert source_metadata_type.__class__.__name__ == "JSONB"


def test_benchmark_reference_result_protects_historical_parents() -> None:
    """
    Verify reference-result provenance cannot be damaged by parent deletion.
    """

    for foreign_key in BenchmarkReferenceResult.__table__.foreign_keys:
        assert foreign_key.ondelete == "RESTRICT"


def test_reference_results_are_separate_from_local_runs() -> None:
    """
    Verify published scores are not incorrectly attached to local runs.
    """

    assert "benchmark_run_id" not in BenchmarkReferenceResult.__table__.c
    assert "benchmark_case_result_id" not in BenchmarkReferenceResult.__table__.c


def test_all_benchmark_orm_relationships_configure_successfully() -> None:
    """
    Verify SQLAlchemy can fully configure every benchmark ORM mapper.

    Metadata-only tests can confirm tables, columns, and foreign keys without
    fully validating relationship ``back_populates`` pairs.

    Explicit mapper configuration catches missing or mismatched relationship
    properties before application or seed code attempts a database query.
    """

    configure_mappers()

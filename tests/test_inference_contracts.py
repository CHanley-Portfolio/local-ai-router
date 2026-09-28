"""
Tests for backend-independent inference contracts.
"""

from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from local_ai_router.inference import InferenceRequest, InferenceResult


def test_inference_request_uses_explicit_application_fields() -> None:
    """
    Verify benchmark-relevant generation settings have stable field names.
    """

    inference_request = InferenceRequest(
        model_name="test-model",
        user_message="Test prompt",
        thinking_enabled=True,
        temperature=Decimal("0.2"),
        top_p=Decimal("0.9"),
        seed=42,
        max_output_tokens=512,
    )

    assert inference_request.model_name == "test-model"
    assert inference_request.user_message == "Test prompt"
    assert inference_request.thinking_enabled is True
    assert inference_request.temperature == Decimal("0.2")
    assert inference_request.top_p == Decimal("0.9")
    assert inference_request.seed == 42
    assert inference_request.max_output_tokens == 512


def test_inference_request_optional_generation_settings_default_to_none() -> None:
    """
    Verify normal chat requests do not require benchmark configuration.
    """

    inference_request = InferenceRequest(
        model_name="test-model",
        user_message="Hello",
        thinking_enabled=False,
    )

    assert inference_request.temperature is None
    assert inference_request.top_p is None
    assert inference_request.seed is None
    assert inference_request.max_output_tokens is None
    assert inference_request.backend_options is None


def test_inference_result_preserves_benchmark_metrics() -> None:
    """
    Verify normalized results can carry benchmark performance telemetry.
    """

    inference_result = InferenceResult(
        model_name="test-model",
        response_text="answer",
        total_duration_ns=10,
        model_load_duration_ns=2,
        prompt_token_count=20,
        prompt_eval_duration_ns=3,
        output_token_count=15,
        output_eval_duration_ns=5,
    )

    assert inference_result.total_duration_ns == 10
    assert inference_result.model_load_duration_ns == 2
    assert inference_result.prompt_token_count == 20
    assert inference_result.prompt_eval_duration_ns == 3
    assert inference_result.output_token_count == 15
    assert inference_result.output_eval_duration_ns == 5


def test_inference_request_is_immutable() -> None:
    """
    Verify a request cannot change after benchmark execution begins.
    """

    inference_request = InferenceRequest(
        model_name="test-model",
        user_message="Hello",
        thinking_enabled=False,
    )

    with pytest.raises(FrozenInstanceError):
        inference_request.model_name = "different-model"  # type: ignore[misc]


def test_inference_result_is_immutable() -> None:
    """
    Verify recorded inference telemetry cannot be mutated accidentally.
    """

    inference_result = InferenceResult(
        model_name="test-model",
        response_text="answer",
    )

    with pytest.raises(FrozenInstanceError):
        inference_result.response_text = "changed"  # type: ignore[misc]

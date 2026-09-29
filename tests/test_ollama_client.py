"""
Tests for the Ollama inference adapter.

These tests verify translation between Local AI Router inference contracts and
Ollama's backend-specific HTTP API without requiring a running Ollama service
or a loaded model.
"""

import asyncio
from decimal import Decimal

import httpx

from local_ai_router.inference import InferenceRequest, OllamaClient


def test_ollama_client_translates_inference_request() -> None:
    """
    Verify normalized inference settings become the expected Ollama payload.

    The rest of the application should only understand InferenceRequest.
    Ollama-specific fields such as ``think`` and ``num_predict`` must remain
    inside the adapter.
    """

    captured_request_json: dict = {}

    async def handle_request(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request_json

        captured_request_json = __import__("json").loads(request.content.decode("utf-8"))

        return httpx.Response(
            status_code=200,
            json={
                "model": "test-model",
                "message": {
                    "role": "assistant",
                    "content": "test response",
                },
            },
        )

    async def execute_test() -> None:
        ollama_client = OllamaClient(
            base_url="http://test-ollama",
        )

        await ollama_client._client.aclose()

        ollama_client._client = httpx.AsyncClient(
            base_url="http://test-ollama",
            transport=httpx.MockTransport(handle_request),
        )

        try:
            await ollama_client.chat(
                InferenceRequest(
                    model_name="test-model",
                    user_message="Test prompt",
                    thinking_enabled=True,
                    temperature=Decimal("0.2"),
                    top_p=Decimal("0.9"),
                    seed=42,
                    max_output_tokens=512,
                    backend_options={
                        "num_ctx": 8192,
                    },
                )
            )
        finally:
            await ollama_client.close()

    asyncio.run(execute_test())

    assert captured_request_json["model"] == "test-model"
    assert captured_request_json["stream"] is False
    assert captured_request_json["think"] is True

    assert captured_request_json["messages"] == [
        {
            "role": "user",
            "content": "Test prompt",
        }
    ]

    assert captured_request_json["options"]["temperature"] == 0.2
    assert captured_request_json["options"]["top_p"] == 0.9
    assert captured_request_json["options"]["seed"] == 42
    assert captured_request_json["options"]["num_predict"] == 512
    assert captured_request_json["options"]["num_ctx"] == 8192


def test_ollama_client_normalizes_response_metrics() -> None:
    """
    Verify Ollama telemetry is translated into InferenceResult fields.
    """

    async def handle_request(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={
                "model": "test-model",
                "message": {
                    "role": "assistant",
                    "content": "Normalized answer",
                },
                "total_duration": 9_000_000,
                "load_duration": 1_000_000,
                "prompt_eval_count": 25,
                "prompt_eval_duration": 2_000_000,
                "eval_count": 40,
                "eval_duration": 5_000_000,
                "done": True,
                "done_reason": "stop",
            },
        )

    async def execute_test():
        ollama_client = OllamaClient(
            base_url="http://test-ollama",
        )

        await ollama_client._client.aclose()

        ollama_client._client = httpx.AsyncClient(
            base_url="http://test-ollama",
            transport=httpx.MockTransport(handle_request),
        )

        try:
            return await ollama_client.chat(
                InferenceRequest(
                    model_name="test-model",
                    user_message="Test prompt",
                    thinking_enabled=False,
                )
            )
        finally:
            await ollama_client.close()

    inference_result = asyncio.run(execute_test())

    assert inference_result.model_name == "test-model"
    assert inference_result.response_text == "Normalized answer"

    assert inference_result.total_duration_ns == 9_000_000
    assert inference_result.model_load_duration_ns == 1_000_000

    assert inference_result.prompt_token_count == 25
    assert inference_result.prompt_eval_duration_ns == 2_000_000

    assert inference_result.output_token_count == 40
    assert inference_result.output_eval_duration_ns == 5_000_000

    assert inference_result.backend_metrics == {
        "done": True,
        "done_reason": "stop",
    }


def test_explicit_inference_settings_override_backend_options() -> None:
    """
    Verify normalized application fields cannot be silently overridden.

    backend_options is an escape hatch for settings that do not yet have a
    normalized field. Explicit normalized fields remain authoritative.
    """

    captured_request_json: dict = {}

    async def handle_request(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request_json

        captured_request_json = __import__("json").loads(request.content.decode("utf-8"))

        return httpx.Response(
            status_code=200,
            json={
                "model": "test-model",
                "message": {
                    "role": "assistant",
                    "content": "answer",
                },
            },
        )

    async def execute_test() -> None:
        ollama_client = OllamaClient(
            base_url="http://test-ollama",
        )

        await ollama_client._client.aclose()

        ollama_client._client = httpx.AsyncClient(
            base_url="http://test-ollama",
            transport=httpx.MockTransport(handle_request),
        )

        try:
            await ollama_client.chat(
                InferenceRequest(
                    model_name="test-model",
                    user_message="Test prompt",
                    thinking_enabled=False,
                    temperature=Decimal("0.2"),
                    max_output_tokens=256,
                    backend_options={
                        "temperature": 1.5,
                        "num_predict": 999,
                        "num_ctx": 8192,
                    },
                )
            )
        finally:
            await ollama_client.close()

    asyncio.run(execute_test())

    assert captured_request_json["options"]["temperature"] == 0.2
    assert captured_request_json["options"]["num_predict"] == 256

    # Backend-only options still survive normally.
    assert captured_request_json["options"]["num_ctx"] == 8192

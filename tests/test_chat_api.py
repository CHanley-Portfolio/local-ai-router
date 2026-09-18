"""
Integration tests for the Local AI Router /chat API endpoint

These tests verify the complete application path between:

    
    HTTP request
        ↓
    ChatRequest validation
        ↓
    routing policy
        ↓
    OllamaClient invocation
        ↓
    ChatResponse serialization

The real ollama service is deliberatly mocked in this test module.

That gives us several important benefits:

    - Tests remain fast.
    - Tests do not require a model to be loaded.
    - Tests do not consume GPU resources.
    - Tests remain deterministic.
    - Failures can be attributed to our application code rather than an external inference service.

A seperate end-to-end smoke test will verify communication with the real Ollama service after tehse integration tests pass.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from local_ai_router.config import DEFAULT_MODEL
from local_ai_router.main import app
from local_ai_router.ollama_client import OllamaClient

@pytest.fixture
def chat_test_client():
    """
    Create a FastAPI TestClient backed by a mocked OllamaClient.

    The Local AI Router normally creates its OllamaClient inside the application's lifespan handler:

        app.state.ollama = OllamaClient()
    
    For these tests, we replace that constructor with a mock before FastAPI starts.

    This allows the application itself to run normally while preventing any real network requests from being sent to Ollama.

    Yields:
        tuple[TestClient, MagicMock]
            The first value is the HTTP test client used to call FastAPI.

            The second value is the mocked OllamaClient instance so each test can inspect exactly how the router attempted to perform inference.
    """

    # MagicMock gives us an object with teh same public inference as
    # OllamaClient without creating the real HTTPX client
    mocked_ollama_client = MagicMock(spec=OllamaClient)

    # Both chat() and close() are asynchronous methods in OllamaClient,
    # so AsyncMock is required rather than a normal MagicMock.
    mocked_ollama_client.chat = AsyncMock()
    mocked_ollama_client.close = AsyncMock()

    # main.py imports OllamaClient directly, so we patch the name where
    # the FastAPI lifespan function actually looks it up
    with patch(
        "local_ai_router.main.OllamaClient",
        return_value = mocked_ollama_client,
    ):
        # Entering TestCLient starts FastAPI's lifespan handler.
        #
        # Because OllamaClient is patched above, app.state.ollama recieves
        # our mocked lient rather than a real Ollama connection
        with TestClient(app) as test_client:
            yield test_client, mocked_ollama_client

def test_chat_fast_route_uses_non_thinking_inference(chat_test_client) -> None:
    """
    Verify that explicit fast routing disables Ollama thinking mode.

    This test protects the complete translation:

        route_mode="fast"
            ↓
        RoutingDecision.thinking_enabled=False
            ↓
        OllamaClient.chat(..., think=False)

    It also verified that routing metadata is returned to the caller.
    """

    test_client, mocked_ollama_client = chat_test_client

    user_message = "What does CUDA stand for?"
    model_name = "test-model"

    # Simulate the JSON structure returnedby Ollama's /api/chat endpoint.
    mocked_ollama_client.chat.return_value = {
        "model": model_name,
        "message": {
            "role": "assistant",
            "content": "CUDA stands for Compute Unified Device Architecture.",
        },
        "total_duration": 1_000_000,
        "eval_count": 12,
        "eval_duration": 500_000,
    }

    response = test_client.post(
        "/chat",
        json={
            "user_message": user_message,
            "model_name": model_name,
            "route_mode": "fast",
        },
    )

    assert response.status_code == 200

    response_body = response.json()

    assert response_body["model_name"] == model_name
    assert response_body["route_mode"] == "fast"
    assert response_body["thinking_enabled"] is False
    assert response_body["route_reason"] == "Fast mode explicitly requested."
    assert response_body["response"] == "CUDA stands for Compute Unified Device Architecture."
    assert response_body["total_duration_ns"] == 1_000_000
    assert response_body["eval_count"] == 12
    assert response_body["eval_duration_ns"] == 500_000

    # Most importatly, verify the boundary between our router and Ollama.
    #
    # The public API exposes logical route_mode values, while the Ollama
    # adapter recieves the backend-specific Boolean 'think' value.
    mocked_ollama_client.chat.assert_awaited_once_with(
        model=model_name,
        user_message=user_message,
        think=False,
    )

def test_chat_reasoning_route_enables_thinking_inference(chat_test_client) -> None:
    """
    Verify that explicit reasoning mode enables Ollama thinking mode.

    This protects the invers of the fast-route behavior and ensures that explicit caller instructions override automatic routing.
    """

    test_client, mocked_ollama_client = chat_test_client

    user_message = "Analyze the trade-offs between these two architectures."
    model_name = "test-model"

    mocked_ollama_client.chat.return_value = {
        "model": model_name,
        "message": {
            "role": "assistant",
            "content": "Here is the architectural analysis"
        },
    }

    response = test_client.post(
        "/chat",
        json={
            "user_message": user_message,
            "model_name": model_name,
            "route_mode": "reasoning"
        },
    )

    assert response.status_code == 200

    response_body = response.json()

    assert response_body["route_mode"] == "reasoning"
    assert response_body["thinking_enabled"] is True
    assert response_body["route_reason"] == "Reasoning mode explicitly requested."

    mocked_ollama_client.chat.assert_awaited_once_with(
        model=model_name,
        user_message=user_message,
        think=True,
    )

def test_chat_uses_default_model_when_model_name_not_specified(chat_test_client) -> None:
    """
    Verify that /chat falls back to DEFAULT_MODEL.

    Clients should not normally need to know which physical model is serving a request.
    If model_name is omitted, the router should use the model configured in config.py
    """

    test_client, mocked_ollama_client = chat_test_client

    user_message = "What does CUDA stand for?"

    mocked_ollama_client.chat.return_value = {
        "model": DEFAULT_MODEL,
        "message": {
            "role": "assistant",
            "content": "CUDA stands for Compute Unified Device Architecture."
        },
    }

    response = test_client.post(
        "/chat",
        json={
            "user_message": user_message,
            "route_mode": "fast",
        },
    )

    assert response.status_code == 200
    assert response.json()["model_name"] == DEFAULT_MODEL

    mocked_ollama_client.chat.assert_awaited_once_with(
        model=DEFAULT_MODEL,
        user_message=user_message,
        think=False,
    )

def test_chat_returns_503_when_ollama_request_fails(chat_test_client) -> None:
    """
    Verify that backend communication failures becaome HTTP 503 responses.

    Ollama is a required downstream service. If it cannot be reached,
    the router should report Service Unavailable rather than exposing an 
    internal HTTPX exception to the API caller.
    """

    test_client, mocked_ollama_client = chat_test_client

    user_message = "What does CUDA stand for?"

    # Construct a representative HTTPX connection failure.
    ollama_request = httpx.Request(
        method="POST",
        url="http://127.0.0.1:11434/api/chat",
    )

    mocked_ollama_client.chat.side_effect = httpx.ConnectError(
        "Unable to connect to Ollama",
        request=ollama_request,
    )

    response = test_client.post(
        "/chat",
        json={
            "user_message": user_message,
            "route_mode": "fast",
        },
    )

    assert response.status_code == 503
    assert response.json() == {"detail": "Ollama request failed."}
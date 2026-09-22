"""
API-level tests for the Local AI Router /route endpoint.

These tests exercise the FastAPI HTTP interface rather than calling the routing-policy function directly.

That distiction is important:
    test_routing.py
        Verifies the routing logic itself.

    test_route_API.py
        Verifies thet HTTP requests are validated correctly, passed into
        the routing layer, and converted into the expected JSON response.

These tests specifically protect our public naming convention:

    user_message
    route_mode
    thinking_enabled
    route_reason

This would catch accidental mistakes such as:

    message vs. user_message
    mode vs route_mode
    think vs thinking_enabled
    reason vs route_reason

No AI interface occurs in these tests and no GPU resources are required.
"""

from fastapi.testclient import TestClient

from local_ai_router.main import app

# TestClient provides an in-process HTTP client for the FastAPI application.
#
# Requests made trhough this object behave similarly to real HTTP requests,
# but the test suite does not need to launvh a separate Uvicorn server.
api_test_client = TestClient(app)


def test_router_api_accepts_current_field_names() -> None:
    """
    Verify that /route accepts the project's standardized request fields.

    Request fields:
        user_message:
            The text that routing policy should inspect.

        route_mode:
            Determines whether rouoting is automatic or explicitly selected.

    Expected Behavior:
        This simple factual question should be classified as fast and should not enable model thinking/reasoning.
    """

    request_body = {
        "user_message": "What does CUDA stand for?",
        "route_mode": "auto",
    }

    response = api_test_client.post("/route", json=request_body)

    # A successful, valid API request should return HTTP 200.
    assert response.status_code == 200

    # Convert the JSON response body into a normal python dictionary
    # so individual response fields can be tested,
    response_data = response.json()

    assert response_data["route_mode"] == "fast"
    assert response_data["thinking_enabled"] is False

    # route_reason is human-readable diagnostic text. Its exact wording may evolve,
    # so verify its meaning rather than requiring an exact sentence.
    assert "reasoning-heavy request" in response_data["route_reason"]


def test_rout_api_selects_reasoning_for_complex_request() -> None:
    """
    Verify that automatic routing works through the HTTP API.

    This messafge deliberately includes several configured reasoning markers:

        analyze
        architecture
        compare
        trade-offs

    The HTTP layer should pass the request into the same routing policy already verified by our lower-level unit tests.
    """

    request_body = {
        "user_message": (
            "Analyze my local AI architecture and compare the trade-offs between using one model and several specialized models"
        ),
        "route_mode": "auto",
    }

    response = api_test_client.post("/route", json=request_body)

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["route_mode"] == "reasoning"
    assert response_data["thinking_enabled"] is True
    assert "reasoning-heavy request" in response_data["route_reason"]


def test_route_api_rejects_old_request_field_names() -> None:
    """
    Verify that obsolete field names are not silently accepted.

    Earlier development versions used inconsistent names such as:

        message
        mode

    Our public API has now standardized on:

        user_message
        route_mode

    This regression test ensures a future refactor cannot accidentally
    restore the older schema without causing the test suite to fail.
    """

    outdated_request_body = {
        "message": "What does CUDA stand for?",
        "mode": "auto",
    }

    response = api_test_client.post(
        "/route",
        json=outdated_request_body,
    )

    # FastAPI/Pydantic uses HTTP 422 when the JSON structure is syntactically
    # valid but does not satisfy the declared request schema.
    assert response.status_code == 422


def test_route_api_rejects_empty_user_message() -> None:
    """
    Verify that an empty user message fails validation.

    RouteRequest defines user_message with a minimum length requirement.
    The request should therefore be rejected before routing logic executes.
    """

    request_body = {
        "user_message": "",
        "route_mode": "auto",
    }

    response = api_test_client.post(
        "/route",
        json=request_body,
    )

    assert response.status_code == 422

"""
Contract tests for the shared routing data models and types.

These tests protect the canonical routing vocabulary used across the Local AI Router.
They are intentionally seperte from the routing-policy tests because they validate the structure of routing contracts
rather than deciding which route a particular prompt should use.
"""

from dataclasses import FrozenInstanceError, fields
from typing import get_args

import pytest

from local_ai_router.routing import RequestMode, RouteMode, RoutingDecision
from local_ai_router.schemas import ChatRequest, ChatResponse, RouteRequest, RouteResponse


def test_route_mode_contains_only_executable_routes() -> None:
    """
    Verify the canonical RouteMode values.

    "auto" is deliberatly excluded because it requests that routing occur;
    it is not itself an executable inference route.
    """

    assert set(get_args(RouteMode)) == {
        "fast",
        "reasoning",
    }


def test_request_mode_contains_supported_client_modes() -> None:
    """
    Verify the canonical routing modes accepted from API/application callers.
    """

    assert set(get_args(RequestMode)) == {
        "auto",
        "fast",
        "reasoning",
    }


def test_routing_decision_uses_standardized_field_names() -> None:
    """
    Protect the canonical RoutingDecision field names.

    This regression test is specifically intended to catch accidental naming
    drift such as:
        rout vs. route_mode
        think vs. thinking_enabled
        reason vs route_reason
    """

    field_names = [field.name for field in fields(RoutingDecision)]

    assert field_names == [
        "route_mode",
        "thinking_enabled",
        "route_reason",
    ]


def test_routing_decision_is_immutable() -> None:
    """
    Verify that routing decisions cannot be modified after construction.
    """

    routing_decision = RoutingDecision(
        route_mode="fast",
        thinking_enabled=False,
        route_reason="fast mode explicitly requested.",
    )

    with pytest.raises(FrozenInstanceError):
        setattr(
            routing_decision,
            "route_mode",
            "reasoning",
        )


def test_api_schemas_use_shared_routing_types() -> None:
    """
    Verify that FastAPI/Pydantic schemas reuse the centralized routing types
    instead of independently defining competing Literal values.
    """

    assert set(get_args(RouteRequest.model_fields["route_mode"].annotation)) == set(
        get_args(RequestMode)
    )

    assert set(get_args(ChatRequest.model_fields["route_mode"].annotation)) == set(
        get_args(RequestMode)
    )

    assert set(get_args(RouteResponse.model_fields["route_mode"].annotation)) == set(
        get_args(RouteMode)
    )

    assert set(get_args(ChatResponse.model_fields["route_mode"].annotation)) == set(
        get_args(RouteMode)
    )

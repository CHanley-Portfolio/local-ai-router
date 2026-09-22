"""
Automated tests for the local AI Routing policy.

These tests verify that routing.py continues producing behavior we expect as teh project evolves.

Routing is particularly important to test because small naming changes or
policy changes can otherwise silently alter which inference mode handles a request

These tests do not:
    - contact Ollama,
    - load an AI model,
    - use the GPU,
    - start FastAPI.

They test teh routing policy directly, which makes them fast and deterministic.
"""

from local_ai_router.routing import choose_route


def test_explicit_fast_route() -> None:
    """
    Verify that explicitly requesting fast mode always selects fast mode.

    THis test confirms three pieces of the RoutingDecison object:
        route_mode:
            must be "fast".

        thinking_enabled:
            Must be "False" because fast mode should not envoke extended reasoning.

        route_reason:
            Must explain that the route was explicitly selected

    Explicit user/application choices should override automatic routing heuristics.
    """

    # Run the routing function with a message that could otherwise be interpreted however the automatic router chooses.
    routing_decision = choose_route(
        user_message="Explain what CUDA is.",
        route_mode="fast",
    )

    # Assert means:
    #
    #       This condition must be true.
    #
    # Ifit is false, pytest marks this test as failed and shows us which expectation was violated.
    assert routing_decision.route_mode == "fast"
    assert routing_decision.thinking_enabled is False
    assert routing_decision.route_reason == "Fast mode explicitly requested."


def test_explicit_reasoning_route() -> None:
    """
    Verify that explicitly requesting reasoning/thinking mode enables reasoning/thinking.

    Explicit reasoning mode should not depend on the wording of the users message.
    the caller has already made the routing decision
    """
    routing_decision = choose_route(
        user_message="What does CUDA stand for?",
        route_mode="reasoning",
    )

    assert routing_decision.route_mode == "reasoning"
    assert routing_decision.thinking_enabled is True
    assert routing_decision.route_reason == "Reasoning mode explicitly requested."


def test_auto_route_selects_fast_for_simple_question() -> None:
    """
    Verify that a straightforward factual question remains on the fast route.

    This protect one of the router's primary goals:
        Do not spend reasoning tokens on ordinary questions
        that do not appear to require deeper analysis
    """

    routing_decision = choose_route(
        user_message="What Does CUDA stand for?",
        route_mode="auto",
    )

    assert routing_decision.route_mode == "fast"
    assert routing_decision.thinking_enabled is False
    assert (
        routing_decision.route_reason
        == "Automatic routing did not detect a reasoning-heavy request."
    )


def test_auto_routing_selects_reasoning_for_complex_request() -> None:
    """
    Verify that automatic recognzes a reasoning heavy request.

    The sample messsage deliberatly contains several markers configured in
    REASONING_MARKERS:
        analyze
        architecture
        compare
        trade-offs

    Finding even one strong marker currently providesenough routing score
    to enable reasoning mode.
    """

    user_message = "Analyze my local AI architecture and compare the trade-offs between using one model and several specialized models."

    routing_decision = choose_route(
        user_message=user_message,
        route_mode="auto",
    )

    assert routing_decision.route_mode == "reasoning"
    assert routing_decision.thinking_enabled is True

    # We do not compare the entire explanation string here because
    # the exact list/order of matched markers may legitimately evolve.
    #
    # Instead, verify that the explanation clearly identifies automatic
    # reasoning routing
    assert "reasoning-heavy request" in routing_decision.route_reason

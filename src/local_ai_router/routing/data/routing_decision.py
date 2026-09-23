"""
Canonical routing-decision data contract.

RoutingDecision represents the result produced by routing policy after a request has been evaluated.

Keeping this object outside the routing algorithm allows other application layers
to depend on teh routing contract without depending on teh current rule-based implementation.
"""

from dataclasses import dataclass

from .routing_types import RouteMode


@dataclass(frozen=True)
class RoutingDecision:
    """
    Represent the result of a routing-policy decision.

    Attributes:
        route_mode:
            Logical inference route selected by the router.

        thinking_enabled:
            Whether the selected route requires reasoning/thinking behavior.

            This is a router-level representation. An inference backend may
            translate this value into a backend-specific parameter.

        route_reason:
            Human-readable explanation describing why the route was selected.

            Keeping this value with teh decision provides observability for
            debugging, testing, benchmarking, and future frontend inspection.

    The dataclass is frozen so routing decisions cannot be accidentally modified after they have been created.
    """

    route_mode: RouteMode
    thinking_enabled: bool
    route_reason: str

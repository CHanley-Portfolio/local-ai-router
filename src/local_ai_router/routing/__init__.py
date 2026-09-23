"""
Public interface for the Local AI Router routing subsystem.

This package seperates routing policy from teh data contracts that describe
routing requests and decisions.

Imports are re-exported here so existing application code can continue using the stable public routing interface.
"""

from .data import RequestMode, RouteMode, RoutingDecision
from .router import choose_route

__all__ = [
    "RequestMode",
    "RouteMode",
    "RoutingDecision",
    "choose_route",
]

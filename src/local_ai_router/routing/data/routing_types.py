"""
Shared routing type definitions for the Local AI Router.

This module provides the cononical string-literal types used by the routing subsystem.
Defining them in one location prevents individual modules from independently recreating the same set of accepted routing values.

These types describe router-level concepts rather than backend-specific settings.
Backend adapters are responsible for the translating router decisions
into parameters required by systems such as Ollama.
"""

from typing import Literal

# RouteMode represents an actual inference route selected by the router.
#
# "auto" is intentionally excluded because it is a request to perform routing
# not an inference route that can execute a model request.
RouteMode = Literal["fast", "reasoning"]

# RequestMode represents the routing modes an application or API caller may request.
#
# "auto" delegates the decision to the router.
# "fast" and "reasoning" explicitly select an inference route.
RequestMode = Literal["auto", "fast", "reasoning"]

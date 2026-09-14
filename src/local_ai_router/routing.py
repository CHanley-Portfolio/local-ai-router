"""
Routing policy for the Local AI Router.

this module contains the logic that decides which interface mode should handle and incoming user request.

At this stage of the project, there are two actual routes:

    Fast: 
        Intended for ordinary questions and lightweight tasks.
        Qwen runs with its thinking/reasoning mode disabled.
    
    Reasoning: 
        Intended for tasks that appear to require deeper analysis.
        Quen runs with thinking/reasoning mode enabled.

The public API also supports an "auto" mode. "auto" is not itself a route.
Instead, it tells the router to inspect the user's message and choose either "fast" or "reasoning".

This first implementation deliberately uses transparent rule-based routing.
That makes the decision process:
    - fast,
    - deterministic,
    - easy to test,
    - easy to understand, 
    - and easy to improve later.

Future versions may use additional signals such as model availability, hardware load, token count, project context, task classification models,
or evaluation data.
"""

from dataclasses import dataclass
from typing import Literal

#-----------------------------------------------------------------------------------------------
# Type aliases
#-----------------------------------------------------------------------------------------------
#
# Literal restricts these string values to a known set of valid choices.
#
# For example, RouteName should only ever contain:
#
#   - "fast"
#   - "reasoning"
#
# This improves readability and allows editors/type checkers to catch accidental values such a as "quick" or "reason".
#
RouteName = Literal["fast", "reasoning"]

# RequestMode represents the values a client is allowed to request.
#
# "auto" means the router decides.
# "fast" and "reasoning" force a particular route.
#
RequestMode = Literal["auto", "fast", "reasoning"]

@dataclass(frozen=True)
class RoutingDecision:
    """
    Represents the result of evaluating a user request and deciding which route should handle it.

    Attributes:
        route_name (RouteName): Tthe logical route selected by the router.
            Current Values:
                - "fast": for ordinary questions and lightweight tasks.
                - "reasoning": for tasks that appear to require deeper analysis.
        think (bool): Whether the selected route should run in thinking/reasoning mode.
            Current Values:
                - True: thinking/reasoning mode enabled.
                - False: thinking/reasoning mode disabled.
        reason (str): A human-readable explanation of why this route was chosen.
            This is deliberatly included so that routing decisions are inspectable rather than behaving as a black box.

    The dataclass is marked frozen=True so a routing decision cannot be accidentaly modified after it has been created.
    """
    route_name: RouteName
    think: bool
    reason: str

#-----------------------------------------------------------------------------------------------
# Automatic-routing indicators
#-----------------------------------------------------------------------------------------------
#
# These words and phrases are currently traeted as strong indicators that 
# a task may benefit from deeper reasoning.
#
# Each match contributes points to a simple routing score inside
# choose_route().
#
# This is intentionally a conservative starting list. We will update it 
# using real project workloads rather than trying to predict every possible request in advance,
#
REASONING_MARKERS = (
    "analyze",
    "analyzing",
    "analysis",
    "architecture",
    "compare",
    "debug",
    "design",
    "diagnose",
    "evaluate",
    "reason through",
    "root cause",
    "step by step",
    "trade-offs",
    "tradeoffs",
    "troubleshoot",
)

def choose_route(user_message: str, requested_mode: RequestMode) -> RoutingDecision:
    """
    Decide which route should handle a user request.

    Args:
        user_message (str): The text of the user's request.
        requested_mode (RequestMode): The mode requested by the client.
            - "auto": router decides based on the content of the message.
            - "fast": force the fast route.
            - "reasoning": force the reasoning route.

    Returns:
        RoutingDecision: The result of evaluating the request and deciding which route should handle it.
            -route_name (RouteName): "fast" or "reasoning"
            -think (bool): Boolean passed to the model backend.
            -reason (str): Explanation of why the route was selected.

     Routing algorithm:
        1. Respect explicit "fast" or "reasoning" requests immediately.
        2. For "auto", normalize the message to lowercase.
        3. Search for known reasoning-related words/phrases.
        4. Add small scores for unusually long prompts.
        5. Route to reasoning if the resulting score reaches the threshold.
        6. Otherwise use the fast route.
    
    Important:
        This function does not call an AI model.

        Routing therefore adds essentially no inference latency and remains
        completely inspectable during this early stage of the project.
    """

    #Explicit modes always take priority over automatic classification.
    #
    # This allows applictions or users to override the router when they 
    # already know which behavior they want.
    if requested_mode == "fast":
        return RoutingDecision(
            route_name="fast",
            think=False,
            reason="Fast mode explicitly requested.",
        )

    if requested_mode == "reasoning":
        return RoutingDecision(
            route_name="reasoning",
            think=True,
            reason="Reasoning mode explicitly requested.",
        )

    # Convert the incomoing message to lowercase so marker comparisons are case-sensitive.
    #
    # For example:
    #   "Analyze this" -> "analyze this"
    # should behave identically.
    normalized_message = user_message.lower()

    # score accumulates evidence that the user request may benefit from deeper reasoning.
    score = 0

    # matched_markers is retained so we can explain the routing decision
    # to the caller rather than simply eturning an unexplained result.
    matched_markers: list[str] = []

    # Search the request for each known reasoning indicator.
    #
    # Each marker is worth two points. Because the current threshold is 
    # also two points, one strong marker is enough to select reasoning mode.
    for marker in REASONING_MARKERS:
        if marker in normalized_message:
            score += 2
            matched_markers.append(marker)

    # Count whitespace-seperated words.
    #
    # Prompt length alone is only weak evidence o difficulty, so a long
    # message contributes one additional point.
    word_count = len(normalized_message.split())
    if word_count >= 150:
        score += 1

    # Character Length gives us another simple measure of a large prompt.
    #
    # Again, this contributes only one point because a long message can be
    #simple--for example, a request summarizing a long document.
    if len(normalized_message) >= 800:
        score += 1

    # Two points currently represent the threshold for reasoning mode.
    #
    # One strong marker reaches the threshold immediately.
    # Alternatively, multiple weaker length indicators can combine.
    if score >= 2:
        marker_text = ", ".join(matched_markers)

        reason = "Automatic routing detected a reasoning-heavy request."

        # If markers were found, include them in the explanation returned
        # by the API. this will becaome useful when debugging routing errors.
        if marker_text:
            reason += f" Matched markers: {marker_text}."

        return RoutingDecision(
            route_name="reasoning",
            think=True,
            reason=reason,
        )

    # If none of the criteria crossed our threshold, use normal fast inference.
    #This is delberately the default because thinking mode is far more expensive for routine queries
    #based on our benchamarks.
    return RoutingDecision(
        route_name="fast",
        think=False,
        reason="Automatic routing did not detect a reasoning-heavy request.",
    )
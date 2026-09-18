"""
Main FastPAI application for the Local AI Router.

This module defines the HTTP-facing service.

Current API endpoints:

    GET /health
        Confirms that the router is running and that Ollama is reachable.

    GET /models
        Returns the model inventory reported by Ollama
    
    POST /route
        Runs routing policy only.
        No AI inference occurs.

    POST /chat
        Routes a user request and sends it to Ollama for inference.

The Application deliberatly keps routing policy and Ollama communication in seperate modules:

    main.py
        HTTP/API orchestration
    
    routing.py
        Routing decisions
    
    ollama_client.py
        Communication with Ollama

    schemas.py
        API data validation

This seperation will make it much easier to add additional models, infernce engines,
memory, tools, and project-specific routing later.
"""
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Request

from .config import DEFAULT_MODEL
from .ollama_client import OllamaClient
from .routing import choose_route
from .schemas import (
    ChatRequest, 
    ChatResponse,
    RouteRequest,
    RouteResponse)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage resources that should exist for the entire router process.

    Parameters:
        app:
            The FastAPI application instnace currently starting or stopping.
    
    Startup behavior:
        Creates one OllamaClient and stores it in:

            app.state.ollama
        
        All API requests reuse this client and its HTTP connection pool.

    Shutdown behaivor:
        Closes the HTTPX client cleanly when FastAPI shuts down.

    Why hhs exists:
        Creating completely new HTTP client for every inference request
        would repeatedly establish connection resources and would make the application less efficient.

        Kepping one client for the application's lifetime is cleaner and scales better
        as the router recieves more requests.

    Yields:
        Control back to FastAPI while the application is running.
    """

    # Create our shared Ollama API client during application startup.
    app.state.ollama = OllamaClient()

    # Everything before yield runs during startup.
    # EVerything after yield runs during shutdown.
    yield

    # Gracefully release the HTTP connections maintained by HTTPX.
    await app.state.ollama.close()

# Create the FastAPI appplication object used by uvicorn.
#
# Version 0.2.0 represents the first version containing actual routing logic.
app = FastAPI(
    title="Local AI Router",
    description="Local routing layer for AI models and services.",
    version="0.2.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health(request: Request):
    """
    Check both router and Ollama for availability.

    Parameters:
        request:
            FastAPI request object.

            We use request.app.state to access the shared OllamaClient
            created during application startup.

    Returns:
        dict:
            Basic health information including:
                router status
                router version
                ollama status
                ollama version

    Raises:
        HTTPException 503:
            Returned if Ollama cannot be reached.
    
    A successful responce means not only that FastAPI is running, 
    but also that the ruter can communicate with its current inference backend.
    """

    try:
        # Ask Ollama for its version as a lightweight connectivity check.
        version = await request.app.state.ollama.version()

    except httpx.HTTPError as exc:
        # 503 Service Unavailable communicates that the router itself is
        # alive, but a required downstream service is unavailable.
        raise HTTPException(
            status_code=503,
            detail="Ollama is unavailable.",
        ) from exc

    return {
        "router": "ok",
        "router_version": app.version,
        "ollama": "ok",
        "ollama_version": version.get("version"),
    }


@app.get("/models")
async def models(request: Request):
    """
    Return the model inventory exposed by Ollama.

    Parameters:
        request:
            FastAPI request object used to retrieve the shared OllamaClient.

    Returns:
        dict:
            The model-list JSON returned by Ollama's /api/tags endpoint.

    Raises:
        HTTPException 503:
            Returned when Ollama cannot supply the model inventory.
    
    **This endpoint currently exposes Ollama's raw model information. 
    A later version will likely provide a router-specific model registy
    instead of exposing backend details directly to applications.**
    """

    try:
        return await request.app.state.ollama.models()
    
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=503,
            detail="Unable to retrieve Ollama models.",
        ) from exc

@app.post("/route", response_model=RouteResponse)
async def route(payload: RouteRequest):
    """
    Evaluate routing policy withoou runnng model inference.

    Parameters:
        payload:
            Validated RouteRequest containing:
                user_message:
                    Text to classify.
                route_mode:
                    auto, fast, or reasoning.
    
    Returns
        RouteResponse:
            Selected route, thinking setting, and explanation.
    
            This endpoint is intentionally seperate from /chat.

            It allows us to test routing logic quickly without:
                - loading a model,
                - consuming gpu time,
                - genereating tokens, 
                - or waiting for an AI response.
        
    It will also become useful for automated routing evaluations.
    """

    # Delegate classification entirely to the routing-policy module.
    decision = choose_route(
        user_message=payload.user_message,
        route_mode=payload.route_mode,
    )

    return RouteResponse(
        route_mode=decision.route_mode,
        thinking_enabled=decision.thinking_enabled,
        route_reason=decision.route_reason,
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    request: Request,
):
    """
    Route a chat and execute it through Ollama.

    Parameters:
        payload:
            Validated CHatRequest containing the user's prompt,
            optional model override, and te requested routing mode
        
        request:
            FastAPI request object used to access the shared OllamaClient.

    Returns:
        ChatResponse:
            Contains both:
                - routing metadata
                - and the model-genereated answer.

    Raises:
        HTTPException 503:
            Returned when communication with Ollama fails.

    Processing sequence:
        1. Resolve which model should be used.
        2. Ask routing policy whether fast or reasoning is appropriate.
        3. Translate that decision into Ollama's thinking_mode Boolean.
        4. Send Request to Ollama. 
        5. Return the answer plus routing/performance information.
    """

    # Use an explicitly requested model when supplied
    #
    # Otherwise fall back to the systems configured default model.
    model_name = payload.model_name or DEFAULT_MODEL

    # Decide whether this request should use normal fast inference
    # or reasoning/thinking behavior
    decision = choose_route(
        user_message=payload.user_message,
        route_mode=payload.route_mode,
    )

    try:
        # Send the actual inference request to Ollama.
        #
        # The API caller does not need to understand Ollama's "thinking_enabled"
        # implementation. Our router derives it from the logical route.
        result = await request.app.state.ollama.chat(
            model=model_name,
            user_message=payload.user_message,
            think=decision.thinking_enabled,
        )

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=503,
            detail="Ollama request failed.",
        ) from exc

    # COnvert Ollama's backend-specific response into our own stable router response schema
    #
    # This abstraction means applications can continue using our API 
    # even if we replace or add another inference backend later.
    return ChatResponse(
        model_name=result.get("model", model_name),
        route_mode=decision.route_mode,
        thinking_enabled=decision.thinking_enabled,
        route_reason=decision.route_reason,
        response=result["message"]["content"],
        total_duration_ns=result.get("total_duration"),
        eval_count=result.get("eval_count"),
        eval_duration_ns=result.get("eval_duration"),
    )

from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Request

from .config import DEFAULT_MODEL
from .ollama_client import OllamaClient
from .schemas import ChatRequest, ChatResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.ollama = OllamaClient()

    yield

    await app.state.ollama.close()


app = FastAPI(
    title="Local AI Router",
    description="Local routing layer for AI models and services.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health(request: Request):
    try:
        version = await request.app.state.ollama.version()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=503,
            detail="Ollama is unavailable.",
        ) from exc

    return {
        "router": "ok",
        "ollama": "ok",
        "ollama_version": version.get("version"),
    }


@app.get("/models")
async def models(request: Request):
    try:
        return await request.app.state.ollama.models()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=503,
            detail="Unable to retrieve Ollama models.",
        ) from exc


@app.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    request: Request,
):
    model = payload.model or DEFAULT_MODEL

    try:
        result = await request.app.state.ollama.chat(
            model=model,
            message=payload.message,
            think=payload.think,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=503,
            detail="Ollama request failed.",
        ) from exc

    return ChatResponse(
        model=result.get("model", model),
        response=result["message"]["content"],
        total_duration_ns=result.get("total_duration"),
        eval_count=result.get("eval_count"),
        eval_duration_ns=result.get("eval_duration"),
    )

from typing import Any

import httpx

from .config import OLLAMA_BASE_URL


class OllamaClient:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=OLLAMA_BASE_URL,
            timeout=httpx.Timeout(
                120.0,
                connect=5.0,
            ),
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def version(self) -> dict[str, Any]:
        response = await self._client.get("/api/version")
        response.raise_for_status()
        return response.json()

    async def models(self) -> dict[str, Any]:
        response = await self._client.get("/api/tags")
        response.raise_for_status()
        return response.json()

    async def chat(
        self,
        model: str,
        user_message: str,
        think: bool,
    ) -> dict[str, Any]:
        response = await self._client.post(
            "/api/chat",
            json={
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": user_message,
                    }
                ],
                "think": think,
                "stream": False,
            },
        )

        response.raise_for_status()
        return response.json()

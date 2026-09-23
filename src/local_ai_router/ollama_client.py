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
        model_name: str,
        user_message: str,
        thinking_enabled: bool,
    ) -> dict[str, Any]:
        """
        Send a chat request to Ollama.

        Args:
            model_name:
                Backend model identifier Ollama should use for inference.

            user_message:
                User prompt that should be sent to model.

            thinking_enabled:
                Router-level reaoning setting.

                The adapter translates this descriptive application field into Ollama's backend-specific 'think' request property.

        Returns:
            dict[str, Any]:
                raw JSON responce returned by Ollama.

        Raises:
            httpx.HTTPError:
                Propagated when communication with Ollama fails or Ollama returns and unsuccessful HTTP response.
        """
        response = await self._client.post(
            "/api/chat",
            json={
                "model": model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": user_message,
                    }
                ],
                "think": thinking_enabled,
                "stream": False,
            },
        )

        response.raise_for_status()
        return response.json()

from typing import Any

import httpx

from .data import InferenceRequest, InferenceResult


class OllamaClient:
    def __init__(
        self,
        base_url: str,
    ) -> None:
        """
        Create an Ollama inference adapter.

        Args:
            base_url:
                Base HTTP URL of the Ollama service.

                Service-specific configuration remains outside this shared
                inference package. The router, benchmark service, or another
                caller supplies the appropriate endpoint.
        """

        self._client = httpx.AsyncClient(
            base_url=base_url,
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
        inference_request: InferenceRequest,
    ) -> InferenceResult:
        """
        Execute one chat inference request through Ollama.

        The Local AI Router passes a backend-independent InferenceRequest.
        This adapter translates those settings into Ollama's API format and then
        converts Ollama's raw JSON response into a stable InferenceResult.

        Args:
            inference_request:
                Normalized model request containing the prompt, model identity,
                reasoning setting, and optional generation parameters.

        Returns:
            InferenceResult:
                Backend-independent model output and available performance
                telemetry.

        Raises:
            httpx.HTTPError:
                Propagated if Ollama cannot be reached or returns an unsuccessful
                HTTP response.
        """

        ollama_options: dict[str, Any] = {}

        if inference_request.backend_options is not None:
            ollama_options.update(inference_request.backend_options)

        if inference_request.temperature is not None:
            ollama_options["temperature"] = float(inference_request.temperature)

        if inference_request.top_p is not None:
            ollama_options["top_p"] = float(inference_request.top_p)

        if inference_request.seed is not None:
            ollama_options["seed"] = inference_request.seed

        if inference_request.max_output_tokens is not None:
            ollama_options["num_predict"] = inference_request.max_output_tokens

        request_payload: dict[str, Any] = {
            "model": inference_request.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": inference_request.user_message,
                }
            ],
            "think": inference_request.thinking_enabled,
            "stream": False,
        }

        if ollama_options:
            request_payload["options"] = ollama_options

        response = await self._client.post(
            "/api/chat",
            json=request_payload,
        )

        response.raise_for_status()

        ollama_response = response.json()

        return InferenceResult(
            model_name=ollama_response.get(
                "model",
                inference_request.model_name,
            ),
            response_text=ollama_response["message"]["content"],
            total_duration_ns=ollama_response.get("total_duration"),
            model_load_duration_ns=ollama_response.get("load_duration"),
            prompt_token_count=ollama_response.get("prompt_eval_count"),
            prompt_eval_duration_ns=ollama_response.get("prompt_eval_duration"),
            output_token_count=ollama_response.get("eval_count"),
            output_eval_duration_ns=ollama_response.get("eval_duration"),
            backend_metrics={
                key: value
                for key, value in ollama_response.items()
                if key
                not in {
                    "model",
                    "message",
                    "total_duration",
                    "load_duration",
                    "prompt_eval_count",
                    "prompt_eval_duration",
                    "eval_count",
                    "eval_duration",
                }
            },
        )

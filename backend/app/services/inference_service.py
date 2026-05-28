import httpx
from typing import Any, Optional

from app.config import settings

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"


async def call_groq(
    messages: list[dict[str, str]],
    model: str,
    max_tokens: Optional[int],
    temperature: Optional[float],
) -> dict[str, Any]:
    """Call Groq chat completions API and return the JSON response."""
    if not settings.GROQ_API_KEY:
        raise RuntimeError("Inference service is not configured")

    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload: dict[str, Any] = {"model": model, "messages": messages}
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    if temperature is not None:
        payload["temperature"] = temperature

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(GROQ_CHAT_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

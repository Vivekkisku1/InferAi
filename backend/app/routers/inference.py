# routers/inference.py
# Main inference endpoint — OpenAI compatible
# Validates API key, calls Groq, logs usage, deducts credits

import logging
import time

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user_from_api_key
from app.models.user import User
from app.services.inference_service import call_groq
from app.services.usage_service import calculate_cost, save_usage_log

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1", tags=["Inference"])


class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = "llama-3.3-70b-versatile"
    messages: list[Message]
    temperature: float = 0.7
    max_tokens: int = 1024


@router.post("/chat/completions")
async def chat_completions(
    req: ChatCompletionRequest,
    auth: tuple = Depends(get_current_user_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    user, api_key_id = auth

    if float(user.credits) <= 0:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient credits. Please top up your account.",
        )

    messages = [{"role": m.role, "content": m.content} for m in req.messages]

    start_time = time.time()
    result = None

    try:
        result = await call_groq(
            messages=messages,
            model=req.model,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
        )
    except Exception:
        latency_ms = int((time.time() - start_time) * 1000)
        await save_usage_log(
            db=db,
            user_id=str(user.id),
            api_key_id=api_key_id,
            model_id=req.model,
            input_tokens=0,
            output_tokens=0,
            latency_ms=latency_ms,
            status="error",
            error_message="provider_error",
        )
        raise HTTPException(status_code=502, detail="Model provider error")

    latency_ms = int((time.time() - start_time) * 1000)

    usage = result.get("usage", {})
    input_tokens = usage.get("prompt_tokens", 0)
    output_tokens = usage.get("completion_tokens", 0)

    await save_usage_log(
        db=db,
        user_id=str(user.id),
        api_key_id=api_key_id,
        model_id=req.model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        status="success",
    )

    cost = calculate_cost(req.model, input_tokens, output_tokens)
    new_credits = float(user.credits) - cost
    await db.execute(
        update(User).where(User.id == user.id).values(credits=new_credits)
    )

    return result


@router.get("/models")
async def list_models():
    return {
        "data": [
            {"id": "llama-3.3-70b-versatile", "provider": "groq"},
            {"id": "llama-3.1-8b-instant", "provider": "groq"},
            {"id": "mixtral-8x7b-32768", "provider": "groq"},
        ]
    }

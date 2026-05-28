# services/usage_service.py
# Handles saving every inference call to the database
# This is the foundation of your billing system

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.usage_log import UsageLog

logger = logging.getLogger(__name__)

# Cost per 1000 tokens in USD for each model
# Adjust these based on what Groq charges you + your margin
MODEL_COSTS = {
    "llama-3.3-70b-versatile": {
        "input_per_1k": 0.00059,
        "output_per_1k": 0.00079,
        "markup": 1.3,
    },
    "llama-3.1-8b-instant": {
        "input_per_1k": 0.00005,
        "output_per_1k": 0.00008,
        "markup": 1.3,
    },
    "mixtral-8x7b-32768": {
        "input_per_1k": 0.00024,
        "output_per_1k": 0.00024,
        "markup": 1.3,
    },
}


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost in USD for a given model and token counts."""
    config = MODEL_COSTS.get(
        model,
        {
            "input_per_1k": 0.001,
            "output_per_1k": 0.001,
            "markup": 1.3,
        },
    )
    cost = (
        (input_tokens / 1000 * config["input_per_1k"])
        + (output_tokens / 1000 * config["output_per_1k"])
    ) * config["markup"]
    return round(cost, 8)


async def save_usage_log(
    db: AsyncSession,
    user_id: str,
    api_key_id: str,
    model_id: str,
    input_tokens: int,
    output_tokens: int,
    latency_ms: int,
    status: str = "success",
    error_message: Optional[str] = None,
) -> Optional[UsageLog]:
    """Save a usage log entry to the database."""
    try:
        cost = calculate_cost(model_id, input_tokens, output_tokens)

        log = UsageLog(
            user_id=user_id,
            api_key_id=api_key_id,
            model_id=model_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_cost_usd=cost,
            latency_ms=latency_ms,
            status=status,
            error_message=error_message,
        )
        db.add(log)
        await db.flush()

        logger.info(
            "Usage logged — user=%s model=%s tokens=%s+%s cost=$%s",
            user_id,
            model_id,
            input_tokens,
            output_tokens,
            cost,
        )
        return log

    except Exception:
        logger.exception("Failed to save usage log")
        return None


async def list_usage_logs(
    db: AsyncSession,
    user_id: str,
    *,
    limit: int = 50,
    offset: int = 0,
) -> list[UsageLog]:
    """List usage history for the usage router."""
    limit = min(max(limit, 1), 100)
    offset = max(offset, 0)
    result = await db.execute(
        select(UsageLog)
        .where(UsageLog.user_id == user_id)
        .order_by(UsageLog.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())

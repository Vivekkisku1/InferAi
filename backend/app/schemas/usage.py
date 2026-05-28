from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UsageLogResponse(BaseModel):
    id: str
    model_id: str
    input_tokens: int
    output_tokens: int
    total_cost_usd: float
    latency_ms: int
    status: str
    api_key_id: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UsageHistoryResponse(BaseModel):
    items: list[UsageLogResponse]
    limit: int
    offset: int
    count: int

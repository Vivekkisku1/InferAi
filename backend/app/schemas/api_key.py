from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional

class APIKeyCreate(BaseModel):
    name: str

class APIKeyResponse(BaseModel):
    id: UUID
    name: str
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

class APIKeyCreated(APIKeyResponse):
    key: str

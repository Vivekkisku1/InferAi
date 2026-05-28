import re
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from uuid import UUID

class UserRegister(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("At least 8 characters required")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Must contain uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Must contain a number")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: str
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

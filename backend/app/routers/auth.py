from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin as LoginRequest, UserResponse, Token
from app.services.auth_service import register_user, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=201)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    try:
        user = await register_user(db, data.email, data.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    token = create_access_token(str(user.id))
    return Token(access_token=token, user=UserResponse.model_validate(user))


@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.email == data.email)
    )

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    access_token = create_access_token(str(user.id))

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

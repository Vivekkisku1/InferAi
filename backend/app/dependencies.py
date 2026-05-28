import hashlib
from dataclasses import dataclass
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.api_key import APIKey

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


@dataclass
class ApiKeyAuth:
    user: User
    api_key_id: str

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    exc = HTTPException(status_code=401, detail="Could not validate credentials")
    if not token:
        raise exc
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise exc
    except JWTError:
        raise exc
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise exc
    return user

async def get_api_key_auth(
    api_key: str = Security(api_key_header),
    db: AsyncSession = Depends(get_db),
) -> ApiKeyAuth:
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    result = await db.execute(
        select(APIKey).where(APIKey.key_hash == key_hash, APIKey.is_active == True)
    )
    api_key_obj = result.scalar_one_or_none()
    if not api_key_obj:
        raise HTTPException(status_code=401, detail="Invalid API key")
    result = await db.execute(select(User).where(User.id == api_key_obj.user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")
    return ApiKeyAuth(user=user, api_key_id=str(api_key_obj.id))


async def get_user_from_api_key(auth: ApiKeyAuth = Depends(get_api_key_auth)) -> User:
    return auth.user


async def get_current_user_from_api_key(
    auth: ApiKeyAuth = Depends(get_api_key_auth),
) -> tuple[User, str]:
    """Return (user, api_key_id) for inference routes."""
    return auth.user, auth.api_key_id

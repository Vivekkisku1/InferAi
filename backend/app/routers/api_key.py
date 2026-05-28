from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.api_key import APIKeyCreate, APIKeyResponse, APIKeyCreated
from app.services.api_key_service import create_api_key, list_api_keys, delete_api_key

router = APIRouter(prefix="/api-keys", tags=["api-keys"])

@router.post("", response_model=APIKeyCreated, status_code=201)
async def create_key(data: APIKeyCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    api_key, raw_key = await create_api_key(db, str(current_user.id), data.name)
    return APIKeyCreated(id=api_key.id, name=api_key.name, is_active=api_key.is_active, created_at=api_key.created_at, key=raw_key)

@router.get("", response_model=list[APIKeyResponse])
async def list_keys(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await list_api_keys(db, str(current_user.id))

@router.delete("/{key_id}", status_code=204)
async def delete_key(key_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    deleted = await delete_api_key(db, key_id, str(current_user.id))
    if not deleted:
        raise HTTPException(status_code=404, detail="API key not found")

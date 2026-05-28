import secrets, hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.api_key import APIKey

def generate_api_key():
    raw = "sk-" + secrets.token_urlsafe(32)
    key_prefix = raw[:12] + "****"
    return raw, hashlib.sha256(raw.encode()).hexdigest(), key_prefix

async def create_api_key(db, user_id, name):
    raw_key, key_hash, key_prefix = generate_api_key()
    api_key = APIKey(user_id=user_id, key_hash=key_hash, key_prefix=key_prefix, name=name)
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)
    return api_key, raw_key

async def list_api_keys(db, user_id):
    result = await db.execute(select(APIKey).where(APIKey.user_id == user_id, APIKey.is_active == True))
    return result.scalars().all()

async def delete_api_key(db, key_id, user_id):
    result = await db.execute(select(APIKey).where(APIKey.id == key_id, APIKey.user_id == user_id))
    api_key = result.scalar_one_or_none()
    if not api_key:
        return False
    api_key.is_active = False
    await db.commit()
    return True

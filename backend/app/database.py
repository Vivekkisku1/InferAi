import logging
from typing import AsyncGenerator
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from app.config import settings

logger = logging.getLogger(__name__)


def _build_async_database_url(url: str) -> str:
    return url.replace("postgresql://", "postgresql+asyncpg://").replace("postgres://", "postgresql+asyncpg://")


engine: AsyncEngine = create_async_engine(
    _build_async_database_url(settings.DATABASE_URL),
    echo=settings.DB_ECHO_SQL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


redis_pool = None
redis_client = None


def create_redis_pool():
    return aioredis.ConnectionPool.from_url(
        settings.REDIS_URL,
        max_connections=settings.REDIS_MAX_CONNECTIONS,
        decode_responses=True,
    )


def get_redis():
    if redis_client is None:
        raise RuntimeError("Redis not initialized")
    return redis_client


async def init_db() -> None:
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection established")
            if settings.is_development:
                await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        logger.critical(f"❌ Database connection failed: {e}")
        raise


async def init_redis() -> None:
    global redis_pool, redis_client
    try:
        redis_pool = create_redis_pool()
        redis_client = aioredis.Redis(connection_pool=redis_pool)
        await redis_client.ping()
        logger.info("✅ Redis connection established")
    except Exception as e:
        logger.critical(f"❌ Redis connection failed: {e}")
        raise


async def close_db() -> None:
    await engine.dispose()
    logger.info("🔌 Database connections closed")


async def close_redis() -> None:
    global redis_client, redis_pool
    if redis_client:
        await redis_client.aclose()
    if redis_pool:
        await redis_pool.aclose()
    logger.info("🔌 Redis connections closed") 
    # Import all models so SQLAlchemy knows about them
from app.models.user import User
from app.models.api_key import APIKey
from app.models.usage_log import UsageLog
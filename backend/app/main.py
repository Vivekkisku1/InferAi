import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import init_db, init_redis, close_db, close_redis, get_redis
from app.middleware.rate_limit import RateLimitMiddleware

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME}")
    await init_db()
    await init_redis()
    logger.info("All systems ready")
    yield
    await close_db()
    await close_redis()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)

# Routers
from app.routers import auth, api_key, inference, usage
app.include_router(auth.router)
app.include_router(api_key.router)
app.include_router(inference.router)
app.include_router(usage.router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "internal_server_error"},
    )

@app.get("/ping")
async def ping():
    return {"status": "ok"}

@app.get("/health")
async def health_check():
    health = {
        "status": "ok",
        "version": settings.APP_VERSION,
        "services": {"database": "unknown", "redis": "unknown"},
    }
    try:
        from sqlalchemy import text
        from app.database import engine
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        health["services"]["database"] = "healthy"
    except Exception:
        health["services"]["database"] = "unhealthy"
        health["status"] = "degraded"
    try:
        redis = get_redis()
        await redis.ping()
        health["services"]["redis"] = "healthy"
    except Exception:
        health["services"]["redis"] = "unhealthy"
        health["status"] = "degraded"
    status_code = 200 if health["status"] == "ok" else 503
    return JSONResponse(content=health, status_code=status_code)

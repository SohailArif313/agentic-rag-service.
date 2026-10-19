import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.errors import register_error_handlers
from app.api.rate_limit import RateLimiter
from app.api.routes import router
from app.config import get_settings

logging.basicConfig(level=logging.INFO)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.rate_limiter = RateLimiter(
        per_minute=settings.rate_limit_per_minute,
        daily_cap=settings.daily_request_cap,
    )
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

register_error_handlers(app)
app.include_router(router)
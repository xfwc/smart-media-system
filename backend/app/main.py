from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.redis import init_redis, close_redis
from app.db.mongodb import init_mongodb, close_mongodb
from app.core.logging import setup_logging_middleware
from app.core.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_redis()
    await init_mongodb()
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()
    await close_redis()
    await close_mongodb()


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging (only if MongoDB available)
try:
    from app.core.logging import log_request_middleware
    app.middleware("http")(log_request_middleware)
except Exception:
    pass


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}


# Routers — import only after app is created
from app.api.user.auth import router as auth_router
from app.api.user.profile import router as profile_router
from app.api.hot.routes import router as hot_router
from app.api.recommend.routes import router as recommend_router
from app.api.plan.routes import router as plan_router
from app.api.idea.routes import router as idea_router
from app.api.admin.routes import router as admin_router

app.include_router(auth_router, prefix=settings.API_V1_PREFIX, tags=["Auth"])
app.include_router(profile_router, prefix=settings.API_V1_PREFIX, tags=["User"])
app.include_router(hot_router, prefix=settings.API_V1_PREFIX, tags=["Hot"])
app.include_router(recommend_router, prefix=settings.API_V1_PREFIX, tags=["Recommend"])
app.include_router(plan_router, prefix=settings.API_V1_PREFIX, tags=["Plan"])
app.include_router(idea_router, prefix=settings.API_V1_PREFIX, tags=["Idea"])
app.include_router(admin_router, prefix=settings.API_V1_PREFIX, tags=["Admin"])

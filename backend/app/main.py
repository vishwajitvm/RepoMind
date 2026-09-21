import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.api.routes import router as api_router

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("repomind")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database schema is initialized on startup
    logger.info("Initializing database schema...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema initialized successfully")
    except Exception as e:
        logger.warning(f"Database schema initialization warning: {e}")

    yield

    # Cleanup resources
    logger.info("Shutting down RepoMind API engine...")
    await engine.dispose()


app = FastAPI(
    title="RepoMind API",
    description="AI Codebase Intelligence Platform with LangGraph, Qdrant, GitHub MCP, and LLM Router",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware for React frontend
cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
if not cors_origins:
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# RepoMind descriptive HTTP request telemetry middleware
try:
    from app.services.telemetry_middleware import RepoMindHTTPTelemetryMiddleware
    app.add_middleware(RepoMindHTTPTelemetryMiddleware)
except Exception as e:
    logger.warning(f"Could not load RepoMindHTTPTelemetryMiddleware: {e}")

# Include API endpoints
app.include_router(api_router, prefix="/api")

# TraceNest Observability UI
try:
    from tracenest.ui.router import router as tracenest_ui_router, tracenest_app_js, tracenest_styles_css
    from fastapi.responses import RedirectResponse

    app.include_router(tracenest_ui_router)

    @app.get("/tracenest", include_in_schema=False)
    async def tracenest_slash_redirect():
        """Redirect /tracenest to /tracenest/ to ensure relative assets load properly."""
        return RedirectResponse(url="/tracenest/", status_code=307)

    @app.get("/styles.css", include_in_schema=False)
    def root_styles_css_fallback():
        """Fallback for relative styles.css request."""
        return tracenest_styles_css()

    @app.get("/app.js", include_in_schema=False)
    def root_app_js_fallback():
        """Fallback for relative app.js request."""
        return tracenest_app_js()

    logger.info("TraceNest UI successfully mounted at /tracenest/")
except Exception as e:
    logger.warning(f"Could not mount TraceNest UI router: {e}")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "RepoMind API",
        "environment": settings.ENVIRONMENT
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

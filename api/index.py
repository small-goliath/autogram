from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import get_settings
from core.database import close_db
from backend.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    print(f"Starting {settings.PROJECT_NAME}")
    yield
    print(f"Shutting down {settings.PROJECT_NAME}")
    await close_db()


def create_application() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Instagram link sharing and comment exchange service",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root() -> dict:
        """Root endpoint."""
        return {
            "message": "Welcome to Autogram API",
            "docs": "/docs",
            "version": "1.0.0"
        }

    return app


app = create_application()
app.include_router(api_router, prefix="/api")
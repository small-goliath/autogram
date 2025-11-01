from fastapi import APIRouter


from backend.routes import admin, public
from core.config import get_settings

settings = get_settings()

api_router = APIRouter()
api_router.include_router(
    public.router,
    tags=["public"]
)
api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"]
)
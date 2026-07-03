"""Vision2 인바운드 HTTP 라우터 조립."""

from fastapi import APIRouter

from apps.vision2.adapter.inbound.api.v1.vision_router import vision_router

vision2_router = APIRouter(prefix="/api/vision2", tags=["vision2"])
vision2_router.include_router(vision_router)

__all__ = ["vision2_router"]

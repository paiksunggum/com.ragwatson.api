from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from apps.vision2.adapter.inbound.api.schemas.vision_schema import (
    VisionImageUploadResponseSchema,
    VisionIntroduceResponseSchema,
)
from apps.vision2.app.dtos.vision_dto import (
    VisionImageUploadCommand,
    VisionIntroduceQuery,
)
from apps.vision2.app.ports.input.vision_use_case import VisionUseCase
from apps.vision2.dependencies.vision_provider import get_vision_use_case

logger = logging.getLogger("apps")
vision_router = APIRouter(prefix="/vision", tags=["vision2"])


@vision_router.get("/myself", response_model=VisionIntroduceResponseSchema)
async def introduce_myself(
    use_case: VisionUseCase = Depends(get_vision_use_case),
) -> VisionIntroduceResponseSchema:
    logger.info("[vision2] Vision 서비스 자기소개 요청")
    result = await use_case.introduce_myself(VisionIntroduceQuery(id=1, name="Vision"))
    return VisionIntroduceResponseSchema(id=result.id, name=result.name)


@vision_router.post("/imageupload", response_model=VisionImageUploadResponseSchema)
async def upload_image(
    file: UploadFile = File(...),
    use_case: VisionUseCase = Depends(get_vision_use_case),
) -> VisionImageUploadResponseSchema:
    if not file.filename:
        raise HTTPException(status_code=400, detail="파일 이름이 없습니다.")
    content_type = file.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(
            status_code=400, detail="이미지 파일만 업로드할 수 있습니다."
        )

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="빈 파일입니다.")

    result = await use_case.upload_image(
        VisionImageUploadCommand(
            filename=file.filename,
            content_type=content_type,
            content=raw,
        )
    )
    return VisionImageUploadResponseSchema(
        fileName=result.filename,
        contentType=result.content_type,
        size=result.size,
        url=result.url,
    )

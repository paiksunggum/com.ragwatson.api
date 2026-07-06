from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from apps.vision2.adapter.inbound.api.schemas.yolo_schema import (
    YoloPredictionResponseSchema,
)
from apps.vision2.app.dtos.yolo_dto import YoloPredictionCommand
from apps.vision2.app.ports.input.yolo_use_case import YoloUseCase
from apps.vision2.dependencies.yolo_provider import get_yolo_use_case

logger = logging.getLogger("apps")
yolo_router = APIRouter(prefix="/yolo", tags=["vision2-yolo"])


@yolo_router.post("/predict", response_model=YoloPredictionResponseSchema)
async def predict_face(
    file: UploadFile = File(...),
    use_case: YoloUseCase = Depends(get_yolo_use_case),
) -> YoloPredictionResponseSchema:
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

    try:
        result = await use_case.predict(
            YoloPredictionCommand(
                filename=file.filename,
                content_type=content_type,
                image_bytes=raw,
            )
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return YoloPredictionResponseSchema(
        predicted_name=result.predicted_name,
        confidence=result.confidence,
    )

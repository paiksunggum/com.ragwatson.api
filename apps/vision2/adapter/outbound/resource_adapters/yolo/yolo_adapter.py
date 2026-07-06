from __future__ import annotations

import asyncio
import io
from pathlib import Path

from PIL import Image
from ultralytics import YOLO

from apps.vision2.app.dtos.yolo_dto import YoloPredictionResult
from apps.vision2.app.ports.output.yolo_port import YoloPort

_WEIGHTS_PATH = (
    Path(__file__).resolve().parents[4]
    / "resources"
    / "yolo_train"
    / "runs"
    / "face_recognition"
    / "weights"
    / "best.pt"
)


class YoloAdapter(YoloPort):
    def __init__(self) -> None:
        self._model: YOLO | None = None

    def _get_model(self) -> YOLO:
        if self._model is None:
            if not _WEIGHTS_PATH.exists():
                raise RuntimeError(
                    f"학습된 얼굴 인식 모델이 없습니다: {_WEIGHTS_PATH}. "
                    "먼저 학습을 실행하세요."
                )
            self._model = YOLO(str(_WEIGHTS_PATH))
        return self._model

    async def predict(self, image_bytes: bytes) -> YoloPredictionResult:
        return await asyncio.to_thread(self._predict, image_bytes)

    def _predict(self, image_bytes: bytes) -> YoloPredictionResult:
        model = self._get_model()
        image = Image.open(io.BytesIO(image_bytes))
        results = model.predict(source=image, verbose=False)
        probs = results[0].probs
        predicted_name = results[0].names[int(probs.top1)]
        confidence = float(probs.top1conf)
        return YoloPredictionResult(
            predicted_name=predicted_name, confidence=confidence
        )

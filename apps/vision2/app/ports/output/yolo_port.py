from __future__ import annotations

from abc import ABC, abstractmethod

from apps.vision2.app.dtos.yolo_dto import YoloPredictionResult


class YoloPort(ABC):
    @abstractmethod
    async def predict(self, image_bytes: bytes) -> YoloPredictionResult:
        """이미지에서 얼굴 인식(분류) 예측 결과를 반환하는 추상 메소드"""
        pass

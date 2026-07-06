from __future__ import annotations

from abc import ABC, abstractmethod

from apps.vision2.app.dtos.yolo_dto import YoloPredictionCommand, YoloPredictionResult


class YoloUseCase(ABC):
    @abstractmethod
    async def predict(self, command: YoloPredictionCommand) -> YoloPredictionResult:
        """업로드된 얼굴 이미지로 인식 예측 실행"""
        pass

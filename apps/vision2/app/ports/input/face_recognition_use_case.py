from __future__ import annotations

from abc import ABC, abstractmethod

from apps.vision2.app.dtos.face_recognition_dto import (
    FaceRecognitionTrainingCommand,
    FaceRecognitionTrainingResult,
)


class FaceRecognitionUseCase(ABC):
    @abstractmethod
    async def train(
        self, command: FaceRecognitionTrainingCommand
    ) -> FaceRecognitionTrainingResult:
        """얼굴 인식(분류) YOLO 모델 파인튜닝 실행"""
        pass

from __future__ import annotations

import asyncio
from pathlib import Path

from ultralytics import YOLO

from apps.vision2.app.dtos.face_recognition_dto import (
    FaceRecognitionTrainingCommand,
    FaceRecognitionTrainingResult,
)
from apps.vision2.app.ports.input.face_recognition_use_case import (
    FaceRecognitionUseCase,
)
from apps.vision2.app.ports.output.face_dataset_port import FaceDatasetPort


class FaceRecognitionInteractor(FaceRecognitionUseCase):
    def __init__(self, dataset_port: FaceDatasetPort) -> None:
        self._dataset_port = dataset_port

    async def train(
        self, command: FaceRecognitionTrainingCommand
    ) -> FaceRecognitionTrainingResult:
        dataset_root = self._dataset_port.get_dataset_root_path()
        return await asyncio.to_thread(self._train, dataset_root, command)

    def _train(
        self, dataset_root: str, command: FaceRecognitionTrainingCommand
    ) -> FaceRecognitionTrainingResult:
        model = YOLO(command.pretrained_weights)
        results = model.train(
            data=dataset_root,
            epochs=command.epochs,
            batch=command.batch_size,
            imgsz=command.image_size,
            project=str(Path(dataset_root) / "runs"),
            name="face_recognition",
            exist_ok=True,
        )
        run_dir = str(results.save_dir)
        return FaceRecognitionTrainingResult(
            best_weights_path=f"{run_dir}/weights/best.pt",
            run_dir=run_dir,
            epochs=command.epochs,
        )

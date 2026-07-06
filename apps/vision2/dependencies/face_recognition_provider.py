from __future__ import annotations

from apps.vision2.adapter.outbound.resource_adapters.yolo.face_dataset_adapter import (
    FaceDatasetAdapter,
)
from apps.vision2.app.ports.input.face_recognition_use_case import (
    FaceRecognitionUseCase,
)
from apps.vision2.app.ports.output.face_dataset_port import FaceDatasetPort
from apps.vision2.app.use_cases.face_recognition_interactor import (
    FaceRecognitionInteractor,
)

_face_dataset: FaceDatasetPort = FaceDatasetAdapter()


def get_face_recognition_use_case() -> FaceRecognitionUseCase:
    return FaceRecognitionInteractor(dataset_port=_face_dataset)

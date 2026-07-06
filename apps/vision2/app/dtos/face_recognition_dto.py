from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FaceRecognitionTrainingCommand:
    epochs: int = 50
    batch_size: int = 16
    image_size: int = 224
    pretrained_weights: str = "yolov8n-cls.pt"


@dataclass(frozen=True)
class FaceRecognitionTrainingResult:
    best_weights_path: str
    run_dir: str
    epochs: int

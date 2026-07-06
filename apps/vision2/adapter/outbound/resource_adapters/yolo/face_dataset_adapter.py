from __future__ import annotations

from pathlib import Path

from apps.vision2.app.ports.output.face_dataset_port import FaceDatasetPort

_DATASET_ROOT = Path(__file__).resolve().parents[4] / "resources" / "yolo_train"


class FaceDatasetAdapter(FaceDatasetPort):
    def get_dataset_root_path(self) -> str:
        return str(_DATASET_ROOT)

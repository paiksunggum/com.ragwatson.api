from __future__ import annotations

from abc import ABC, abstractmethod


class FaceDatasetPort(ABC):
    @abstractmethod
    def get_dataset_root_path(self) -> str:
        """YOLO 분류 학습용 얼굴 데이터셋 루트 디렉터리 경로를 반환하는 추상 메소드"""
        pass

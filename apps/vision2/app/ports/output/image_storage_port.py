from __future__ import annotations

from abc import ABC, abstractmethod


class ImageStoragePort(ABC):
    @abstractmethod
    async def upload(self, filename: str, content: bytes, content_type: str) -> str:
        """이미지를 스토리지에 업로드하고 접근 가능한 URL을 반환하는 추상 메소드"""
        pass

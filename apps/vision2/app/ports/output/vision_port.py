from __future__ import annotations

from abc import ABC, abstractmethod

from apps.vision2.app.dtos.vision_dto import (
    VisionImageUploadCommand,
    VisionImageUploadResult,
    VisionIntroduceQuery,
    VisionIntroduceResult,
)


class VisionPort(ABC):
    @abstractmethod
    async def introduce_myself(
        self, query: VisionIntroduceQuery
    ) -> VisionIntroduceResult:
        """Vision 서비스 자기소개 레포지토리 추상 메소드"""
        pass

    @abstractmethod
    async def upload_image(
        self, command: VisionImageUploadCommand
    ) -> VisionImageUploadResult:
        """이미지 업로드 수신 레포지토리 추상 메소드"""
        pass

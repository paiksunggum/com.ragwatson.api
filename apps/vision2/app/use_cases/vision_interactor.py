from __future__ import annotations

from apps.vision2.app.dtos.vision_dto import (
    VisionImageUploadCommand,
    VisionImageUploadResult,
    VisionIntroduceQuery,
    VisionIntroduceResult,
)
from apps.vision2.app.ports.input.vision_use_case import VisionUseCase
from apps.vision2.app.ports.output.vision_port import VisionPort


class VisionInteractor(VisionUseCase):
    def __init__(self, repository: VisionPort) -> None:
        self._repository = repository

    async def introduce_myself(
        self, query: VisionIntroduceQuery
    ) -> VisionIntroduceResult:
        return await self._repository.introduce_myself(query)

    async def upload_image(
        self, command: VisionImageUploadCommand
    ) -> VisionImageUploadResult:
        return await self._repository.upload_image(command)

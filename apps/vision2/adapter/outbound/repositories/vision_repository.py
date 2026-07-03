from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from apps.vision2.app.dtos.vision_dto import (
    VisionImageUploadCommand,
    VisionImageUploadResult,
    VisionIntroduceQuery,
    VisionIntroduceResult,
)
from apps.vision2.app.ports.output.image_storage_port import ImageStoragePort
from apps.vision2.app.ports.output.vision_port import VisionPort

logger = logging.getLogger("apps")


class VisionRepository(VisionPort):
    def __init__(self, session: AsyncSession, storage: ImageStoragePort) -> None:
        self.session = session
        self._storage = storage

    async def introduce_myself(
        self, query: VisionIntroduceQuery
    ) -> VisionIntroduceResult:
        return VisionIntroduceResult(id=query.id, name="Vision 서비스")

    async def upload_image(
        self, command: VisionImageUploadCommand
    ) -> VisionImageUploadResult:
        size = len(command.content)
        logger.info(
            "[VisionRepository] 이미지 업로드 수신 filename=%s content_type=%s size=%d",
            command.filename,
            command.content_type,
            size,
        )
        url = await self._storage.upload(
            command.filename, command.content, command.content_type
        )
        return VisionImageUploadResult(
            filename=command.filename,
            content_type=command.content_type,
            size=size,
            url=url,
        )

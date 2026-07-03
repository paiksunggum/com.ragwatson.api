from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.vision2.adapter.outbound.clients.s3_image_client import S3ImageClient
from apps.vision2.adapter.outbound.repositories.vision_repository import (
    VisionRepository,
)
from apps.vision2.app.ports.input.vision_use_case import VisionUseCase
from apps.vision2.app.ports.output.image_storage_port import ImageStoragePort
from apps.vision2.app.ports.output.vision_port import VisionPort
from apps.vision2.app.use_cases.vision_interactor import VisionInteractor
from core.matrix.oracle_database import get_db

_image_storage: ImageStoragePort = S3ImageClient()


def get_vision_repository(
    db: AsyncSession = Depends(get_db),
) -> VisionPort:
    return VisionRepository(session=db, storage=_image_storage)


def get_vision_use_case(
    repository: VisionPort = Depends(get_vision_repository),
) -> VisionUseCase:
    return VisionInteractor(repository=repository)

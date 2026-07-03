from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.automode.adapter.outbound.clients.bge_m3_embedding_client import (
    BgeM3EmbeddingClient,
)
from apps.automode.adapter.outbound.repositories.email_pgvector_repository import (
    ReceivedEmailPgVectorRepository,
)
from apps.automode.app.ports.input.receiver_use_case import ReceiverUseCase
from apps.automode.app.ports.output.embedding_port import EmbeddingPort
from apps.automode.app.ports.output.receiver_port import ReceiverPort
from apps.automode.app.use_cases.receiver_interactor import ReceiverInteractor
from core.matrix.database_manager import get_db

_embedder: EmbeddingPort = BgeM3EmbeddingClient()


def get_receiver_repository(db: AsyncSession = Depends(get_db)) -> ReceiverPort:
    return ReceivedEmailPgVectorRepository(session=db, embedder=_embedder)


def get_receiver_use_case(
    repository: ReceiverPort = Depends(get_receiver_repository),
) -> ReceiverUseCase:
    return ReceiverInteractor(port=repository)

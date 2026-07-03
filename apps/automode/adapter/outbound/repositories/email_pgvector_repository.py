from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.automode.adapter.outbound.mappers.received_email_mapper import (
    ReceivedEmailMapper,
)
from apps.automode.adapter.outbound.orm.received_email_orm import ReceivedEmailORM
from apps.automode.app.dtos.receiver_dto import ReceivedEmail, ReceivedEmailCommand
from apps.automode.app.ports.output.embedding_port import EmbeddingPort
from apps.automode.app.ports.output.receiver_port import ReceiverPort


class ReceivedEmailPgVectorRepository(ReceiverPort):
    def __init__(self, session: AsyncSession, embedder: EmbeddingPort) -> None:
        self._session = session
        self._embedder = embedder

    async def save(self, command: ReceivedEmailCommand) -> ReceivedEmail:
        if command.message_id:
            existing = await self._session.execute(
                select(ReceivedEmailORM).where(
                    ReceivedEmailORM.message_id == command.message_id
                )
            )
            found = existing.scalar_one_or_none()
            if found is not None:
                return ReceivedEmailMapper.to_entity(found)

        embedding = await self._embedder.embed(f"{command.subject}\n{command.body}")
        orm = ReceivedEmailMapper.to_orm(command, embedding)
        self._session.add(orm)
        await self._session.commit()
        await self._session.refresh(orm)
        return ReceivedEmailMapper.to_entity(orm)

    async def find_all(self) -> list[ReceivedEmail]:
        result = await self._session.execute(
            select(ReceivedEmailORM).order_by(ReceivedEmailORM.received_at.desc())
        )
        return [ReceivedEmailMapper.to_entity(orm) for orm in result.scalars().all()]

from __future__ import annotations

import uuid
from datetime import datetime

from apps.automode.adapter.outbound.orm.received_email_orm import ReceivedEmailORM
from apps.automode.app.dtos.receiver_dto import ReceivedEmail, ReceivedEmailCommand


class ReceivedEmailMapper:
    @staticmethod
    def to_orm(
        command: ReceivedEmailCommand, embedding: list[float]
    ) -> ReceivedEmailORM:
        return ReceivedEmailORM(
            id=str(uuid.uuid4()),
            message_id=command.message_id,
            subject=command.subject,
            body=command.body,
            sender=command.sender,
            source=command.source,
            received_at=datetime.utcnow(),
            embedding=embedding,
        )

    @staticmethod
    def to_entity(orm: ReceivedEmailORM) -> ReceivedEmail:
        return ReceivedEmail(
            id=orm.id,
            subject=orm.subject,
            body=orm.body,
            sender=orm.sender,
            source=orm.source,
            received_at=orm.received_at,
        )

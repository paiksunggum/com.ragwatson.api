from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from apps.automode.adapter.inbound.api.schemas.receiver_schema import (
    ReceivedEmailRequest,
    ReceivedEmailResponse,
)
from apps.automode.app.dtos.receiver_dto import ReceivedEmailCommand
from apps.automode.app.ports.input.receiver_use_case import ReceiverUseCase
from apps.automode.dependencies.receiver_provider import get_receiver_use_case

logger = logging.getLogger("apps")

receiver_router = APIRouter(prefix="/receive", tags=["receiver"])


@receiver_router.post("", response_model=ReceivedEmailResponse)
async def receive_email(
    schema: ReceivedEmailRequest,
    use_case: ReceiverUseCase = Depends(get_receiver_use_case),
) -> ReceivedEmailResponse:
    result = await use_case.receive(
        ReceivedEmailCommand(
            subject=schema.subject,
            body=schema.body,
            sender=schema.sender,
            source=schema.source,
            message_id=schema.message_id,
        )
    )
    logger.info(
        "[receive_email] id=%s subject=%s sender=%s source=%s",
        result.id,
        result.subject,
        result.sender,
        result.source,
    )
    return ReceivedEmailResponse(
        id=result.id,
        subject=result.subject,
        body=result.body,
        sender=result.sender,
        source=result.source,
        received_at=result.received_at,
    )


@receiver_router.get("", response_model=list[ReceivedEmailResponse])
async def list_emails(
    use_case: ReceiverUseCase = Depends(get_receiver_use_case),
) -> list[ReceivedEmailResponse]:
    emails = await use_case.list_emails()
    return [
        ReceivedEmailResponse(
            id=e.id,
            subject=e.subject,
            body=e.body,
            sender=e.sender,
            source=e.source,
            received_at=e.received_at,
        )
        for e in emails
    ]

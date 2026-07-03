import logging

from fastapi import APIRouter, Depends

from apps.automode.adapter.inbound.api.schemas.receiver_schema import (
    ReceivedEmailRequest,
    ReceivedEmailResponse,
)
from apps.automode.adapter.inbound.api.schemas.watcher_schema import (
    WatcherResponseSchema,
    WatcherSchema,
)
from apps.automode.app.dtos.receiver_dto import ReceivedEmailCommand
from apps.automode.app.ports.input.watcher_use_case import WatcherUseCase
from apps.automode.dependencies.watcher_provider import get_watcher_use_case

"""
왓처 (Watcher Hub)
sherlock_homes 커뮤니케이션 스포크의 인바운드 게이트웨이.
단순 라우터가 아닌 'Triage Nurse'(초진 및 분류 관문) 역할을 맡을 예정.

지금은 기본 뼈대(자기소개)만 구현.
Case A(홈즈 처리)/Case B(star_craft 경유 페이커 에스컬레이션) 라우팅 로직은
다음 단계에서 추가.
"""
logger = logging.getLogger("apps")
watcher_router = APIRouter(prefix="/watcher", tags=["watcher"])


@watcher_router.get("/myself", response_model=WatcherResponseSchema)
async def introduce_myself(
    watcher: WatcherUseCase = Depends(get_watcher_use_case),
) -> WatcherResponseSchema:
    result = await watcher.introduce_myself(WatcherSchema(id=1, name="Watcher"))
    return WatcherResponseSchema(id=result.id, name=result.name)


@watcher_router.post("/receive", response_model=ReceivedEmailResponse | None)
async def filter_and_receive(
    schema: ReceivedEmailRequest,
    watcher: WatcherUseCase = Depends(get_watcher_use_case),
) -> ReceivedEmailResponse | None:
    result = await watcher.filter_stop_word(
        ReceivedEmailCommand(
            subject=schema.subject,
            body=schema.body,
            sender=schema.sender,
            source=schema.source,
            message_id=schema.message_id,
        )
    )
    if result is None:
        return None
    return ReceivedEmailResponse(
        id=result.id,
        subject=result.subject,
        body=result.body,
        sender=result.sender,
        source=result.source,
        received_at=result.received_at,
    )

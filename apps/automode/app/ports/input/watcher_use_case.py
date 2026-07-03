from __future__ import annotations

from abc import ABC, abstractmethod

from apps.automode.adapter.inbound.api.schemas.watcher_schema import WatcherSchema
from apps.automode.app.dtos.receiver_dto import ReceivedEmail, ReceivedEmailCommand
from apps.automode.app.dtos.watcher_dto import WatcherResponse


class WatcherUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: WatcherSchema) -> WatcherResponse:
        """왓처(Watcher Hub)의 자기소개 메소드"""
        pass

    @abstractmethod
    async def filter_stop_word(
        self, command: ReceivedEmailCommand
    ) -> ReceivedEmail | None:
        """정지 단어(욕설/비상식 한국어) 필터링 하는 메소드.
        정상 메일만 기존 receiver 파이프라인(pgvector 저장)으로 전달하고,
        욕설/비상식으로 판정되면 None을 반환하여 저장하지 않는다.
        """
        pass

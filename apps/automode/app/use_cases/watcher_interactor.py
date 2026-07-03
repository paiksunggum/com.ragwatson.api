from __future__ import annotations

import logging

from apps.automode.adapter.inbound.api.schemas.watcher_schema import WatcherSchema
from apps.automode.app.dtos.receiver_dto import ReceivedEmail, ReceivedEmailCommand
from apps.automode.app.dtos.watcher_dto import WatcherQuery, WatcherResponse
from apps.automode.app.ports.input.receiver_use_case import ReceiverUseCase
from apps.automode.app.ports.input.watcher_use_case import WatcherUseCase
from apps.automode.app.ports.output.judge_filter_port import JudgeFilterPort
from apps.automode.app.ports.output.watcher_port import WatcherPort

logger = logging.getLogger("apps")


class WatcherInteractor(WatcherUseCase):
    def __init__(
        self,
        repository: WatcherPort,
        judge: JudgeFilterPort,
        receiver: ReceiverUseCase,
    ) -> None:
        self.repository = repository
        self._judge = judge
        self._receiver = receiver

    async def introduce_myself(self, schema: WatcherSchema) -> WatcherResponse:
        return await self.repository.introduce_myself(
            WatcherQuery(id=schema.id, name=schema.name)
        )

    async def filter_stop_word(
        self, command: ReceivedEmailCommand
    ) -> ReceivedEmail | None:
        """정지 단어 필터링 하는 모델"""
        text = f"{command.subject}\n{command.body}"
        is_abusive = await self._judge.is_abusive(text)
        if is_abusive:
            logger.warning(
                "[Watcher] 욕설/비상식 메일 차단 subject=%s sender=%s",
                command.subject,
                command.sender,
            )
            return None

        return await self._receiver.receive(command)

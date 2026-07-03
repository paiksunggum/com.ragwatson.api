from __future__ import annotations

from apps.automode.adapter.inbound.api.schemas.judge_schema import JudgeSchema
from apps.automode.app.dtos.judge_dto import JudgeQuery, JudgeResponse
from apps.automode.app.ports.input.judge_use_case import JudgeUseCase
from apps.automode.app.ports.output.judge_port import JudgePort


class JudgeInteractor(JudgeUseCase):
    def __init__(self, repository: JudgePort) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: JudgeSchema) -> JudgeResponse:
        return await self.repository.introduce_myself(
            JudgeQuery(id=schema.id, name=schema.name)
        )

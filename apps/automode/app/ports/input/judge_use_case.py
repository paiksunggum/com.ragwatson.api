from __future__ import annotations

from abc import ABC, abstractmethod

from apps.automode.adapter.inbound.api.schemas.judge_schema import JudgeSchema
from apps.automode.app.dtos.judge_dto import JudgeResponse


class JudgeUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: JudgeSchema) -> JudgeResponse:
        """저지(Judge)의 자기소개 메소드"""
        pass

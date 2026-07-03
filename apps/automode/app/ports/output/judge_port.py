from __future__ import annotations

from abc import ABC, abstractmethod

from apps.automode.app.dtos.judge_dto import JudgeQuery, JudgeResponse


class JudgePort(ABC):
    @abstractmethod
    async def introduce_myself(self, query: JudgeQuery) -> JudgeResponse:
        """저지(Judge)의 자기소개 레포지토리 추상 메소드"""
        pass

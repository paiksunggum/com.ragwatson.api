from __future__ import annotations

from abc import ABC, abstractmethod


class JudgeFilterPort(ABC):
    @abstractmethod
    async def is_abusive(self, text: str) -> bool:
        """욕설/비상식적 한국어 여부를 판정하는 추상 메소드"""
        pass

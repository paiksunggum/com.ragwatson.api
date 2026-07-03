from __future__ import annotations

from abc import ABC, abstractmethod

from apps.automode.app.dtos.watcher_dto import WatcherQuery, WatcherResponse


class WatcherPort(ABC):
    @abstractmethod
    async def introduce_myself(self, query: WatcherQuery) -> WatcherResponse:
        """왓처(Watcher Hub)의 자기소개 레포지토리 추상 메소드"""
        pass

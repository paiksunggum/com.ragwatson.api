from __future__ import annotations

import logging

from apps.automode.app.dtos.watcher_dto import WatcherQuery, WatcherResponse
from apps.automode.app.ports.output.watcher_port import WatcherPort

logger = logging.getLogger("apps")


class WatcherRepository(WatcherPort):
    async def introduce_myself(self, query: WatcherQuery) -> WatcherResponse:
        logger.info(f"[WatcherRepository] introduce_myself 진입 | request_data={query}")
        return WatcherResponse(id=query.id, name=query.name)

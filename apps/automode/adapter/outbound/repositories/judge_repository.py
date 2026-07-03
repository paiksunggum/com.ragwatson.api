from __future__ import annotations

import logging

from apps.automode.app.dtos.judge_dto import JudgeQuery, JudgeResponse
from apps.automode.app.ports.output.judge_port import JudgePort

logger = logging.getLogger("apps")


class JudgeRepository(JudgePort):
    async def introduce_myself(self, query: JudgeQuery) -> JudgeResponse:
        logger.info(f"[JudgeRepository] introduce_myself 진입 | request_data={query}")
        return JudgeResponse(id=query.id, name=query.name)

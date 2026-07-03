import logging

from fastapi import APIRouter, Depends

from apps.automode.adapter.inbound.api.schemas.judge_schema import (
    JudgeCheckRequest,
    JudgeCheckResponse,
    JudgeResponseSchema,
    JudgeSchema,
)
from apps.automode.app.ports.input.judge_use_case import JudgeUseCase
from apps.automode.app.ports.output.judge_filter_port import JudgeFilterPort
from apps.automode.dependencies.judge_provider import (
    get_judge_filter_port,
    get_judge_use_case,
)

"""
저지 (Judge)
KcELECTRA 파인튜닝 모델로 욕설/비상식 한국어를 판정하는 정책 필터.
"""
logger = logging.getLogger("apps")
judge_router = APIRouter(prefix="/judge", tags=["judge"])


@judge_router.get("/myself", response_model=JudgeResponseSchema)
async def introduce_myself(
    judge: JudgeUseCase = Depends(get_judge_use_case),
) -> JudgeResponseSchema:
    result = await judge.introduce_myself(JudgeSchema(id=1, name="Judge"))
    return JudgeResponseSchema(id=result.id, name=result.name)


@judge_router.post("/check", response_model=JudgeCheckResponse)
async def check(
    schema: JudgeCheckRequest,
    judge: JudgeFilterPort = Depends(get_judge_filter_port),
) -> JudgeCheckResponse:
    is_abusive = await judge.is_abusive(f"{schema.subject}\n{schema.body}")
    return JudgeCheckResponse(is_abusive=is_abusive)

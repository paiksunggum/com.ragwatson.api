from __future__ import annotations

from apps.automode.adapter.outbound.clients.kcelectra_judge_client import (
    KcElectraJudgeClient,
)
from apps.automode.adapter.outbound.repositories.judge_repository import JudgeRepository
from apps.automode.app.ports.input.judge_use_case import JudgeUseCase
from apps.automode.app.ports.output.judge_filter_port import JudgeFilterPort
from apps.automode.app.ports.output.judge_port import JudgePort
from apps.automode.app.use_cases.judge_interactor import JudgeInteractor

_judge_filter: JudgeFilterPort = KcElectraJudgeClient()


def get_judge_repository() -> JudgePort:
    return JudgeRepository()


def get_judge_use_case() -> JudgeUseCase:
    return JudgeInteractor(repository=get_judge_repository())


def get_judge_filter_port() -> JudgeFilterPort:
    return _judge_filter

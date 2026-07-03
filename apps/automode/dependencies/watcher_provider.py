from __future__ import annotations

from fastapi import Depends

from apps.automode.adapter.outbound.repositories.watcher_repository import (
    WatcherRepository,
)
from apps.automode.app.ports.input.receiver_use_case import ReceiverUseCase
from apps.automode.app.ports.input.watcher_use_case import WatcherUseCase
from apps.automode.app.ports.output.judge_filter_port import JudgeFilterPort
from apps.automode.app.ports.output.watcher_port import WatcherPort
from apps.automode.app.use_cases.watcher_interactor import WatcherInteractor
from apps.automode.dependencies.judge_provider import get_judge_filter_port
from apps.automode.dependencies.receiver_provider import get_receiver_use_case


def get_watcher_repository() -> WatcherPort:
    return WatcherRepository()


def get_watcher_use_case(
    repository: WatcherPort = Depends(get_watcher_repository),
    judge: JudgeFilterPort = Depends(get_judge_filter_port),
    receiver: ReceiverUseCase = Depends(get_receiver_use_case),
) -> WatcherUseCase:
    return WatcherInteractor(repository=repository, judge=judge, receiver=receiver)

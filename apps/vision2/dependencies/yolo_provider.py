from __future__ import annotations

from apps.vision2.adapter.outbound.resource_adapters.yolo.yolo_adapter import (
    YoloAdapter,
)
from apps.vision2.app.ports.input.yolo_use_case import YoloUseCase
from apps.vision2.app.ports.output.yolo_port import YoloPort
from apps.vision2.app.use_cases.yolo_interactor import YoloInteractor

_yolo_port: YoloPort = YoloAdapter()


def get_yolo_use_case() -> YoloUseCase:
    return YoloInteractor(yolo_port=_yolo_port)

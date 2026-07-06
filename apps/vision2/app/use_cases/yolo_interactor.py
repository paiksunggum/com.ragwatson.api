from __future__ import annotations

from apps.vision2.app.dtos.yolo_dto import YoloPredictionCommand, YoloPredictionResult
from apps.vision2.app.ports.input.yolo_use_case import YoloUseCase
from apps.vision2.app.ports.output.yolo_port import YoloPort


class YoloInteractor(YoloUseCase):
    def __init__(self, yolo_port: YoloPort) -> None:
        self._yolo_port = yolo_port

    async def predict(self, command: YoloPredictionCommand) -> YoloPredictionResult:
        return await self._yolo_port.predict(command.image_bytes)

from .lyra_service import LyraService
from .schemas import ChatRequest, ChatResponse


class ChloeController:
    def __init__(self) -> None:
        self.service = LyraService()

    def chat(self, req: ChatRequest) -> ChatResponse:
        answer = self.service.reply(req)
        return ChatResponse(answer=answer)

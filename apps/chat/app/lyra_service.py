from .iris_model import IrisModel
from .schemas import ChatMessage, ChatRequest


class LyraService:
    def __init__(self) -> None:
        self.model = IrisModel()

    def _to_thread(self, req: ChatRequest) -> list[ChatMessage]:
        if req.messages:
            return list(req.messages)
        if req.message and req.message.strip():
            return [ChatMessage(role="user", text=req.message.strip())]
        raise ValueError("message 또는 messages 가 필요합니다.")

    def reply(self, req: ChatRequest) -> str:
        thread = self._to_thread(req)
        last = thread[-1]
        if last.role != "user":
            raise ValueError("마지막 메시지는 user 여야 합니다.")

        history: list[dict] = []
        for msg in thread[:-1]:
            role = "user" if msg.role == "user" else "model"
            history.append({"role": role, "parts": [msg.text]})

        model_id = req.model.strip() if req.model and req.model.strip() else None
        return self.model.generate_reply(
            history=history,
            last_user_text=last.text,
            model_name=model_id,
        )

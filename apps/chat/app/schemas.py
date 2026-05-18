from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    text: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    """단일 메시지 또는 대화 기록(마지막은 user)."""

    message: str | None = Field(
        default=None,
        description="한 줄 질문( messages 가 없을 때 사용 )",
    )
    messages: list[ChatMessage] | None = Field(
        default=None,
        description="역할·텍스트 목록; 있으면 이 값이 우선",
    )
    model: str | None = Field(
        default=None,
        description="Gemini 모델 ID (미지정 시 GEMINI_MODEL 환경 변수)",
    )


class ChatResponse(BaseModel):
    answer: str

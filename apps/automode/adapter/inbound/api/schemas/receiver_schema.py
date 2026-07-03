from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ReceivedEmailRequest(BaseModel):
    subject: str = ""
    body: str = ""
    sender: str = ""
    source: str = "unknown"
    message_id: str | None = None


class ReceivedEmailResponse(BaseModel):
    id: str
    subject: str
    body: str
    sender: str
    source: str
    received_at: datetime

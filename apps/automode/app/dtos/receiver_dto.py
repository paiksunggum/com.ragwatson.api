from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ReceivedEmailCommand:
    subject: str
    body: str
    sender: str
    source: str = "unknown"
    message_id: str | None = None


@dataclass
class ReceivedEmail:
    id: str
    subject: str
    body: str
    sender: str
    source: str
    received_at: datetime = field(default_factory=datetime.utcnow)

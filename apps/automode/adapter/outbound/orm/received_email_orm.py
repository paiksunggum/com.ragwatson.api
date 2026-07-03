from __future__ import annotations

from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from apps.automode.adapter.outbound.clients.bge_m3_embedding_client import EMBEDDING_DIM
from core.matrix.theone_base import TheOneBase


class ReceivedEmailORM(TheOneBase):
    __tablename__ = "automode_received_emails"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    message_id: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    subject: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    sender: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(
        Vector(EMBEDDING_DIM), nullable=False
    )

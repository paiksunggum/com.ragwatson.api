"""Neon(PostgreSQL) 비동기 SQLAlchemy 2.0 — 엔진·세션·Base."""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

_backend_dir = Path(__file__).resolve().parent.parent.parent
load_dotenv(_backend_dir / ".env")

engine: AsyncEngine | None = None
AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = None


class Base(DeclarativeBase):
    pass


def normalize_async_database_url(url: str) -> str:
    """postgres URL을 SQLAlchemy asyncio + psycopg3 드라이버 형식으로 맞춘다."""
    u = url.strip()
    if not u:
        raise ValueError("DATABASE_URL is not set")
    if "+psycopg_async" in u:
        return u
    if u.startswith("postgresql+psycopg://"):
        return u.replace("postgresql+psycopg://", "postgresql+psycopg_async://", 1)
    if u.startswith("postgresql://"):
        return u.replace("postgresql://", "postgresql+psycopg_async://", 1)
    if u.startswith("postgres://"):
        return u.replace("postgres://", "postgresql+psycopg_async://", 1)
    raise ValueError(
        "DATABASE_URL must start with postgresql://, postgres://, or postgresql+psycopg://"
    )


def init_engine() -> None:
    global engine, AsyncSessionLocal
    raw = (os.getenv("DATABASE_URL") or "").strip()
    if not raw or engine is not None:
        return
    engine = create_async_engine(
        normalize_async_database_url(raw),
        echo=False,
        pool_pre_ping=True,
    )
    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autoflush=False,
    )


init_engine()


async def get_db() -> AsyncGenerator[AsyncSession]:
    if AsyncSessionLocal is None:
        init_engine()
    if AsyncSessionLocal is None:
        raise RuntimeError("DATABASE_URL is not set")
    async with AsyncSessionLocal() as session:
        yield session


async def create_all_tables() -> None:
    if engine is None:
        init_engine()
    if engine is None:
        return

    from sqlmodel import SQLModel

    from apps.automode.adapter.outbound.orm.received_email_orm import (
        ReceivedEmailORM,  # noqa: F401
    )
    from apps.sports.app.models.ads_model import Ads  # noqa: F401
    from apps.sports.app.models.practice_model import Practice  # noqa: F401
    from apps.sports.app.models.sports_model import Sports  # noqa: F401
    from apps.sports.app.models.users_model import User  # noqa: F401
    from apps.titanic.adapter.outbound.orm.passenger_jack_trainer_orm import (
        JackTrainerORM,  # noqa: F401
    )
    from apps.titanic.adapter.outbound.orm.passenger_rose_model_orm import (
        RoseModelORM,  # noqa: F401
    )
    from core.matrix.theone_base import TheOneBase

    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(SQLModel.metadata.create_all)
        await conn.run_sync(TheOneBase.metadata.create_all)


async def neon_now(db: AsyncSession) -> dict[str, str]:
    result = await db.execute(text("SELECT NOW() AS now"))
    return {"now": str(result.scalar_one())}


async def dispose_engine() -> None:
    global engine, AsyncSessionLocal
    if engine is not None:
        await engine.dispose()
    engine = None
    AsyncSessionLocal = None

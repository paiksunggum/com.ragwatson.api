import os
from collections.abc import AsyncGenerator
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

_backend_root = Path(__file__).resolve().parent.parent
load_dotenv(_backend_root / ".env")
load_dotenv(find_dotenv(usecwd=True), override=False)

database_url: str | None = (os.getenv("DATABASE_URL") or "").strip() or None

engine = None
AsyncSessionLocal = None

if database_url:
    engine = create_async_engine(database_url, echo=False)
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if AsyncSessionLocal is None:
        raise HTTPException(
            status_code=503,
            detail="DATABASE_URL is not set; add it to backend/.env",
        )
    async with AsyncSessionLocal() as session:
        yield session


async def neon_now(session: AsyncSession) -> dict:
    """DB 연결·시간 조회 (Neon 등 Postgres 헬스체크)."""
    try:
        result = await session.execute(text("SELECT NOW();"))
        now = result.scalar()
        return {
            "status": "success",
            "neon_time": str(now) if now is not None else None,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def dispose_engine() -> None:
    if engine is not None:
        await engine.dispose()

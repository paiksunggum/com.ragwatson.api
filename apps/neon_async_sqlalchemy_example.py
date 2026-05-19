"""
Neon(PostgreSQL) 비동기 접속 예제 — SQLAlchemy 2.0 + psycopg(비동기).

실행 (backend 디렉터리에서):
    python -m apps.neon_async_sqlalchemy_example

backend/.env 에 Neon 대시보드에서 복사한 DATABASE_URL 을 넣으세요.
  예: postgresql://USER:PASSWORD@ep-....neon.tech/neondb?sslmode=require
동기 URL이면 아래 to_async_neon_url() 이 psycopg_async 드라이버용으로 바꿉니다.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

_backend_root = Path(__file__).resolve().parent.parent
load_dotenv(_backend_root / ".env")
load_dotenv(find_dotenv(usecwd=True), override=False)


def to_async_neon_url(url: str) -> str:
    """Neon/일반 postgres URL 을 SQLAlchemy asyncio + psycopg3 형식으로 맞춘다."""
    u = url.strip()
    if not u:
        raise SystemExit(
            "DATABASE_URL 이 비어 있습니다. backend/.env 에 Neon 연결 문자열을 설정하세요."
        )
    if "+psycopg_async" in u:
        return u
    if u.startswith("postgresql+psycopg://"):
        return u.replace("postgresql+psycopg://", "postgresql+psycopg_async://", 1)
    if u.startswith("postgresql://"):
        return u.replace("postgresql://", "postgresql+psycopg_async://", 1)
    if u.startswith("postgres://"):
        return u.replace("postgres://", "postgresql+psycopg_async://", 1)
    raise SystemExit(
        "DATABASE_URL 을 postgresql:// 또는 postgres:// 로 시작하도록 설정하세요."
    )


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    age: Mapped[int]


async def main() -> None:
    raw = (os.getenv("DATABASE_URL") or "").strip()
    database_url = to_async_neon_url(raw)

    engine = create_async_engine(database_url, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        new_user = User(name="홍길동", age=30)
        session.add(new_user)
        await session.commit()

        stmt = select(User).where(User.age >= 20)
        result = await session.execute(stmt)
        users = result.scalars().all()
        for u in users:
            print(f"조회된 유저: {u.name} ({u.age}세)")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

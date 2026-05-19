import os
import sys
from logging.config import fileConfig
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from alembic import context

_backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_backend_root))
load_dotenv(_backend_root / ".env")

from apps.database import normalize_async_database_url  # noqa: E402
from apps.secom.app.models.user import User  # noqa: E402, F401
from sqlmodel import SQLModel  # noqa: E402

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata

_raw_url = (os.getenv("DATABASE_URL") or "").strip()
if _raw_url:
    sync_url = normalize_async_database_url(_raw_url).replace(
        "postgresql+psycopg_async://", "postgresql+psycopg://", 1
    )
    config.set_main_option("sqlalchemy.url", sync_url)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

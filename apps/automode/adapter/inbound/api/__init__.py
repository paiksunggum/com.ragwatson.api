from fastapi import APIRouter

from apps.automode.adapter.inbound.api.v1.discord_router import discord_router
from apps.automode.adapter.inbound.api.v1.email_router import email_router
from apps.automode.adapter.inbound.api.v1.judge_router import judge_router
from apps.automode.adapter.inbound.api.v1.juso_router import juso_router
from apps.automode.adapter.inbound.api.v1.orchestrate_router import orchestrate_router
from apps.automode.adapter.inbound.api.v1.receiver_router import receiver_router
from apps.automode.adapter.inbound.api.v1.telegram_router import telegram_router
from apps.automode.adapter.inbound.api.v1.watcher_router import watcher_router

automode_router = APIRouter(prefix="/api/automode", tags=["automode"])
automode_router.include_router(email_router)
automode_router.include_router(discord_router)
automode_router.include_router(juso_router)
automode_router.include_router(telegram_router)
automode_router.include_router(orchestrate_router)
automode_router.include_router(receiver_router)
automode_router.include_router(watcher_router)
automode_router.include_router(judge_router)

__all__ = ["automode_router"]

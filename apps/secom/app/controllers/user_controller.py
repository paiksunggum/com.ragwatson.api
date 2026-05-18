import logging

from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas import InitDbResponse, UserRegisterRequest, UserResponse
from ..schemas.user_schema import UserSchema
from ..services.user_service import UserService

logger = logging.getLogger(__name__)


class UserController:
    def __init__(self, db: AsyncSession | None = None):
        self.db = db

    def save_user(self, user_schema: UserSchema) -> None:
        logger.info(
            "[UserController] save_user 레이어 진입 — %s",
            user_schema.model_dump(mode="json"),
        )
        UserService().save_user(user_schema)

    async def init_db(self) -> InitDbResponse:
        return InitDbResponse(
            ok=True,
            message="User table init not configured yet",
            seeded=[],
        )

    async def register(self, req: UserRegisterRequest) -> UserResponse:
        return UserResponse(
            id=0,
            user_id=req.user_id,
            email=req.email,
            name=req.name,
            birthdate=req.birthdate,
            gender=req.gender,
            role=req.role,
        )

import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from apps.database import engine

from ..models.user import User  # noqa: F401 — register table on metadata
from ..schemas import InitDbResponse, UserRegisterRequest, UserResponse
from ..schemas.user_schema import UserLoginSchema, UserSchema
from ..services.user_service import UserService

logger = logging.getLogger(__name__)


class UserController:
    def __init__(self, db: AsyncSession):
        self.user_service = UserService(db)

    async def save_user(self, user_schema: UserSchema) -> UserResponse:
        logger.info(
            "[UserController] save_user — %s",
            user_schema.model_dump(mode="json", exclude={"password"}),
        )
        user = await self.user_service.save_user(user_schema)
        return UserResponse.model_validate(user)

    async def login_user(self, login: UserLoginSchema) -> UserResponse:
        logger.info("[UserController] login_user — user_id=%s", login.user_id)
        user = await self.user_service.login_user(login)
        return UserResponse.model_validate(user)

    async def init_db(self) -> InitDbResponse:
        if engine is None:
            raise ValueError("DATABASE_URL is not set")
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        return InitDbResponse(
            ok=True,
            message="users 테이블을 준비했습니다.",
            seeded=[],
        )

    async def register(self, req: UserRegisterRequest) -> UserResponse:
        from ..models.role import UserRole

        return await self.save_user(
            UserSchema(
                user_id=req.user_id,
                password=req.password,
                email=req.email,
                name=req.name,
                birthdate=req.birthdate,
                gender=req.gender,
                role=UserRole(req.role),
            )
        )

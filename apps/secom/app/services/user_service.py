import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User
from ..repositories.user_repository import UserRepository
from ..schemas.user_schema import UserLoginSchema, UserSchema
from ..security import hash_password, verify_password

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.user_repository = UserRepository(session)

    async def save_user(self, user_schema: UserSchema) -> User:
        logger.info(
            "[UserService] save_user — user_id=%s email=%s",
            user_schema.user_id,
            user_schema.email,
        )
        if await self.user_repository.get_by_user_id(user_schema.user_id) is not None:
            raise ValueError("이미 사용 중인 아이디입니다.")

        role = (
            user_schema.role.value
            if hasattr(user_schema.role, "value")
            else str(user_schema.role)
        )
        user = User(
            user_id=user_schema.user_id,
            password_hash=hash_password(user_schema.password),
            email=user_schema.email,
            name=user_schema.name,
            birthdate=user_schema.birthdate,
            gender=user_schema.gender,
            role=role,
        )
        try:
            return await self.user_repository.create(user)
        except IntegrityError as e:
            raise ValueError("이미 사용 중인 아이디입니다.") from e

    async def login_user(self, login: UserLoginSchema) -> User:
        logger.info("[UserService] login_user — user_id=%s", login.user_id)
        user = await self.user_repository.get_by_user_id(login.user_id)
        if user is None:
            user = await self.user_repository.get_by_email(login.user_id)
        if user is None or not verify_password(login.password, user.password_hash):
            raise ValueError("아이디 또는 비밀번호가 올바르지 않습니다.")
        return user

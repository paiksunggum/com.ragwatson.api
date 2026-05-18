import logging

from ..repositories.user_repository import UserRepository
from ..schemas.user_schema import UserSchema

logger = logging.getLogger(__name__)


class UserService:
    def save_user(self, user_schema: UserSchema) -> None:
        logger.info(
            "[UserService] save_user 레이어 진입 — %s",
            user_schema.model_dump(mode="json"),
        )
        UserRepository().save_user(user_schema)

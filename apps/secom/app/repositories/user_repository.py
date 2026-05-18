import logging

from ..schemas.user_schema import UserSchema

logger = logging.getLogger(__name__)


class UserRepository:
    def save_user(self, user_schema: UserSchema) -> None:
        logger.info(
            "[UserRepository] save_user 레이어 진입 — %s",
            user_schema.model_dump(mode="json"),
        )

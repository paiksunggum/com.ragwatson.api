from pydantic import BaseModel

from ..models.role import UserRole


class UserSchema(BaseModel):
    user_id: str
    password: str
    email: str
    name: str
    birthdate: str
    gender: str
    role: UserRole


class UserLoginSchema(BaseModel):
    """로그인 시 레이어 간 전달 (폼 이메일은 user_id에 담음)."""

    user_id: str
    password: str

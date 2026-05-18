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

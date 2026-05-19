from typing import Literal

from pydantic import BaseModel, Field

UserRole = Literal["admin", "user", "athlete"]
Gender = Literal["male", "female", "none"]


class UserRegisterRequest(BaseModel):
    user_id: str = Field(..., min_length=1, description="로그인 아이디 (이메일 형식)")
    password: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    birthdate: str = Field(..., pattern=r"^\d{8}$")
    gender: Gender
    role: UserRole


class UserResponse(BaseModel):
    id: int
    user_id: str
    email: str
    name: str
    birthdate: str
    gender: str
    role: str

    model_config = {"from_attributes": True}


class InitDbResponse(BaseModel):
    ok: bool = True
    message: str
    seeded: list[UserResponse]


class UserLoginResponse(BaseModel):
    ok: bool = True
    message: str = "로그인 요청을 받았습니다."

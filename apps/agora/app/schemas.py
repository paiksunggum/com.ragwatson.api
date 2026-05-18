from typing import Literal

from pydantic import BaseModel, Field


class SignupRequest(BaseModel):
    userId: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    email: str = ""
    name: str = Field(..., min_length=1)
    birthdate: str = Field(..., pattern=r"^\d{8}$")
    gender: Literal["male", "female", "none"]


class SignupResponse(BaseModel):
    ok: bool = True
    message: str = "회원가입 요청을 받았습니다."

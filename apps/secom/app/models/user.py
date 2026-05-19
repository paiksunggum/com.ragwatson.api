from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(max_length=255, unique=True, index=True)
    password_hash: str = Field(max_length=255)
    email: str = Field(max_length=255, index=True)
    name: str = Field(max_length=255)
    birthdate: str = Field(max_length=8)
    gender: str = Field(max_length=16)
    role: str = Field(max_length=32)

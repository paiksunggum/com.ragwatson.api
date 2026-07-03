from pydantic import BaseModel, Field


class JudgeResponseSchema(BaseModel):
    id: int = Field(0, description="Judge ID")
    name: str = Field("Judge", description="Judge's name")


class JudgeSchema(BaseModel):
    id: int = Field(0, description="Judge ID")
    name: str = Field("Judge", description="Judge's name")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "Judge",
            }
        }
    }


class JudgeCheckRequest(BaseModel):
    subject: str = ""
    body: str = ""


class JudgeCheckResponse(BaseModel):
    is_abusive: bool

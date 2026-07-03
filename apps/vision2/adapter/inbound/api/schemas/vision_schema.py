from __future__ import annotations

from pydantic import BaseModel


class VisionIntroduceResponseSchema(BaseModel):
    id: int
    name: str


class VisionImageUploadResponseSchema(BaseModel):
    ok: bool = True
    fileName: str
    contentType: str
    size: int
    url: str

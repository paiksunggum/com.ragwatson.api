from __future__ import annotations

from pydantic import BaseModel


class YoloPredictionResponseSchema(BaseModel):
    predicted_name: str
    confidence: float

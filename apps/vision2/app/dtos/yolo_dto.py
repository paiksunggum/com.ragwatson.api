from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class YoloPredictionCommand:
    filename: str
    content_type: str
    image_bytes: bytes


@dataclass(frozen=True)
class YoloPredictionResult:
    predicted_name: str
    confidence: float

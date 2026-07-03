from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VisionIntroduceQuery:
    id: int
    name: str


@dataclass(frozen=True)
class VisionIntroduceResult:
    id: int
    name: str


@dataclass(frozen=True)
class VisionImageUploadCommand:
    filename: str
    content_type: str
    content: bytes


@dataclass(frozen=True)
class VisionImageUploadResult:
    filename: str
    content_type: str
    size: int
    url: str

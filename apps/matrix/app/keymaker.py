"""전역 API 키·외부 클라이언트(Gemini 등)를 한곳에서 관리."""

from __future__ import annotations

import os
from pathlib import Path

import google.generativeai as genai
from dotenv import find_dotenv, load_dotenv

_keymaker_singleton: Keymaker | None = None


class Keymaker:
    """
    앱 전체에서 쓰는 API 자격 증명과, 그로부터 만든 클라이언트를 보관한다.
    `backend/.env` 를 로드한 뒤 환경 변수를 읽는다.
    """

    def __init__(self) -> None:
        backend_root = Path(__file__).resolve().parents[3]
        load_dotenv(backend_root / ".env")
        load_dotenv(find_dotenv(usecwd=True), override=False)

        self.gemini_api_key: str = (os.getenv("GEMINI_API_KEY") or "").strip()
        self.gemini_model: str = (
            (os.getenv("GEMINI_MODEL") or "gemini-2.5-flash").strip()
        )
        self.openweather_api_key: str = (os.getenv("OPENWEATHER_API_KEY") or "").strip()

        self._gemini: genai.GenerativeModel | None
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self._gemini = genai.GenerativeModel(self.gemini_model)
        else:
            self._gemini = None

    @property
    def gemini(self) -> genai.GenerativeModel | None:
        """키가 없으면 None."""
        return self._gemini

    def require_gemini(self) -> genai.GenerativeModel:
        if self._gemini is None:
            raise ValueError(
                "GEMINI_API_KEY가 설정되어 있지 않습니다. backend/.env 에 추가하세요."
            )
        return self._gemini


def get_keymaker() -> Keymaker:
    """앱 전역 단일 Keymaker 인스턴스를 반환한다."""
    global _keymaker_singleton
    if _keymaker_singleton is None:
        _keymaker_singleton = Keymaker()
    return _keymaker_singleton


def reset_keymaker_for_tests() -> None:
    """테스트 등에서 싱글톤을 비울 때만 사용."""
    global _keymaker_singleton
    _keymaker_singleton = None



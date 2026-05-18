from __future__ import annotations

import httpx

from ...matrix.app.keymaker import get_keymaker

OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


class OpenWeatherReader:
    def __init__(self) -> None:
        self.api_key = get_keymaker().openweather_api_key

    def require_api_key(self) -> str:
        if not self.api_key:
            raise ValueError(
                "OPENWEATHER_API_KEY가 설정되어 있지 않습니다. backend/.env 에 추가하세요."
            )
        return self.api_key

    async def fetch_current(
        self,
        *,
        city: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
    ) -> dict:
        key = self.require_api_key()
        params: dict[str, str | float] = {
            "appid": key,
            "units": "metric",
            "lang": "kr",
        }
        if lat is not None and lon is not None:
            params["lat"] = lat
            params["lon"] = lon
        elif city:
            params["q"] = city
        else:
            raise ValueError("city 또는 lat/lon 이 필요합니다.")

        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(OPENWEATHER_URL, params=params)
            if res.status_code == 404:
                raise ValueError("해당 위치의 날씨를 찾을 수 없습니다.")
            res.raise_for_status()
            return res.json()

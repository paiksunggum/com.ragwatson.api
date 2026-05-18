from .schemas import WeatherResponse
from .weather_service import WeatherService


class WeatherController:
    def __init__(self) -> None:
        self.service = WeatherService()

    async def get_current(
        self,
        *,
        city: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
    ) -> WeatherResponse:
        return await self.service.get_current(city=city, lat=lat, lon=lon)

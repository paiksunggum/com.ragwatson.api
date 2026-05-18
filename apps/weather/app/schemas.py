from pydantic import BaseModel


class WeatherResponse(BaseModel):
    city: str
    temp_c: float
    description: str
    icon: str

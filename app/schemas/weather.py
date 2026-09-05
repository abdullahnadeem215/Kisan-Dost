"""
Weather and climate schemas.
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.evidence import EvidentiaryDomainModel, Evidence


class DailyWeatherForecast(BaseModel):
    date: str
    temp_max: float
    temp_min: float
    precipitation_mm: float
    humidity: float
    wind_speed_kmh: float
    condition: str


class WeatherData(EvidentiaryDomainModel):
    """
    Current weather condition and forecast summary for a given location.
    """
    location: str = Field(..., description="Location name or coordinates label")
    latitude: float = Field(...)
    longitude: float = Field(...)
    temperature_c: float = Field(..., description="Current temperature in Celsius")
    temp_max_c: float = Field(...)
    temp_min_c: float = Field(...)
    humidity_percent: float = Field(..., ge=0.0, le=100.0)
    precipitation_mm: float = Field(..., ge=0.0)
    wind_speed_kmh: float = Field(..., ge=0.0)
    condition: str = Field(..., description="Weather status e.g. Sunny, Rain, Cloudy")
    et0_mm: Optional[float] = Field(None, description="Reference Evapotranspiration ET0 in mm/day")
    status: str = Field(default="🟢 LIVE", description="Data status: 🟢 LIVE or 🟡 CACHED")
    is_live: bool = Field(default=True, description="True if retrieved live from API, False if cached")
    timestamp: Optional[str] = Field(None, description="ISO timestamp of weather observation")
    forecast_5day: List[DailyWeatherForecast] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list, description="Weather data evidence")

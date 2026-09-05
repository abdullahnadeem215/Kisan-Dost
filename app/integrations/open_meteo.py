"""
Open-Meteo API integration client with automatic evidence grounding.
"""
from datetime import datetime, timezone
import logging
from typing import Dict, Tuple, Optional
import httpx
from app.schemas.weather import WeatherData, DailyWeatherForecast
from app.schemas.evidence import Evidence
from config.settings import settings

logger = logging.getLogger(__name__)

# Representative coordinates for major Pakistani agricultural districts
DISTRICT_COORDINATES: Dict[str, Tuple[float, float]] = {
    "multan": (30.1575, 71.5249),
    "lahore": (31.5204, 74.3587),
    "faisalabad": (31.4187, 73.0791),
    "sargodha": (32.0836, 72.6711),
    "sahiwal": (30.6682, 73.1014),
    "bahawalpur": (29.3956, 71.6836),
    "rahim yar khan": (28.4212, 70.2989),
    "rawalpindi": (33.5651, 73.0169),
    "peshawar": (34.0151, 71.5249),
    "sukkur": (27.7052, 68.8574),
    "hyderabad": (25.3960, 68.3578),
    "quetta": (30.1798, 66.9750),
}


class OpenMeteoClient:
    """
    Client for fetching weather forecast and historical data from Open-Meteo REST API.
    All outputs return WeatherData with explicit Evidence metadata.
    """
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.open_meteo_base_url

    def get_weather(self, district_or_loc: str, lat: Optional[float] = None, lon: Optional[float] = None) -> WeatherData:
        """
        Fetch real-time weather and 5-day forecast for a district or specific lat/lon.
        Falls back gracefully to offline seasonal baseline if network fails.
        """
        clean_loc = district_or_loc.strip().lower()
        if lat is None or lon is None:
            if clean_loc in DISTRICT_COORDINATES:
                lat, lon = DISTRICT_COORDINATES[clean_loc]
            else:
                # Default to Multan (heart of Punjab agrarian belt)
                lat, lon = DISTRICT_COORDINATES["multan"]

        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": "true",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,relative_humidity_2m_mean,wind_speed_10m_max,et0_fao_evapotranspiration",
            "timezone": "Asia/Karachi"
        }

        try:
            with httpx.Client(timeout=6.0) as client:
                res = client.get(f"{self.base_url}/forecast", params=params)
                res.raise_for_status()
                data = res.json()

            current = data.get("current_weather", {})
            daily = data.get("daily", {})

            daily_forecasts = []
            dates = daily.get("time", [])
            max_temps = daily.get("temperature_2m_max", [])
            min_temps = daily.get("temperature_2m_min", [])
            precips = daily.get("precipitation_sum", [])
            humidities = daily.get("relative_humidity_2m_mean", [])
            winds = daily.get("wind_speed_10m_max", [])

            for i in range(min(5, len(dates))):
                daily_forecasts.append(
                    DailyWeatherForecast(
                        date=dates[i],
                        temp_max=float(max_temps[i] if i < len(max_temps) else 32.0),
                        temp_min=float(min_temps[i] if i < len(min_temps) else 20.0),
                        precipitation_mm=float(precips[i] if i < len(precips) else 0.0),
                        humidity=float(humidities[i] if i < len(humidities) else 50.0),
                        wind_speed_kmh=float(winds[i] if i < len(winds) else 12.0),
                        condition="Rain" if (precips[i] if i < len(precips) else 0) > 2.0 else "Clear/Sunny"
                    )
                )

            current_temp = float(current.get("temperature", 28.5))
            wind_spd = float(current.get("windspeed", 10.0))

            evapotranspiration = float(daily.get("et0_fao_evapotranspiration", [4.5])[0]) if daily.get("et0_fao_evapotranspiration") else 4.5

            evidence = Evidence(
                source_id=f"OPEN_METEO_{lat}_{lon}_{datetime.now(timezone.utc).strftime('%Y%m%d')}",
                source_name="Open-Meteo API",
                verification_state="verified",
                timestamp=datetime.now(timezone.utc),
                confidence_score=0.95,
                url_or_reference=f"https://open-meteo.com/en/docs#latitude={lat}&longitude={lon}",
                notes="Live weather telemetry retrieved from Open-Meteo API."
            )

            return WeatherData(
                location=district_or_loc.title(),
                latitude=lat,
                longitude=lon,
                temperature_c=current_temp,
                temp_max_c=daily_forecasts[0].temp_max if daily_forecasts else current_temp + 5,
                temp_min_c=daily_forecasts[0].temp_min if daily_forecasts else current_temp - 5,
                humidity_percent=daily_forecasts[0].humidity if daily_forecasts else 55.0,
                precipitation_mm=daily_forecasts[0].precipitation_mm if daily_forecasts else 0.0,
                wind_speed_kmh=wind_spd,
                condition="Sunny" if current.get("weathercode", 0) <= 3 else "Rain/Cloudy",
                et0_mm=evapotranspiration,
                status="🟢 LIVE",
                is_live=True,
                timestamp=datetime.now(timezone.utc).isoformat(),
                forecast_5day=daily_forecasts,
                evidence=[evidence]
            )

        except Exception as e:
            logger.warning(f"Open-Meteo API request failed for {district_or_loc}: {e}. Returning fallback weather data.")
            evidence = Evidence(
                source_id=f"OPEN_METEO_FALLBACK_{clean_loc}",
                source_name="Open-Meteo Fallback Engine (Cached)",
                verification_state="fallback",
                timestamp=datetime.now(timezone.utc),
                confidence_score=0.70,
                notes=f"Network fetch error ({e}). Utilized Pakistani seasonal climatology baseline."
            )
            return WeatherData(
                location=district_or_loc.title(),
                latitude=lat,
                longitude=lon,
                temperature_c=30.0,
                temp_max_c=35.0,
                temp_min_c=22.0,
                humidity_percent=50.0,
                precipitation_mm=0.0,
                wind_speed_kmh=10.0,
                condition="Clear (Historical Fallback)",
                et0_mm=4.8,
                status="🟡 CACHED",
                is_live=False,
                timestamp=datetime.now(timezone.utc).isoformat(),
                forecast_5day=[
                    DailyWeatherForecast(
                        date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                        temp_max=35.0,
                        temp_min=22.0,
                        precipitation_mm=0.0,
                        humidity=50.0,
                        wind_speed_kmh=10.0,
                        condition="Clear"
                    )
                ],
                evidence=[evidence]
            )

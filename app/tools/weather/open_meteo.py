"""
Open-Meteo weather and reference evapotranspiration (ET0) tool.
"""
from typing import Optional
from app.integrations.open_meteo import OpenMeteoClient
from app.tools.weather.geocoder import geocode_location
from app.schemas.weather import WeatherData


def fetch_weather_report(
    location: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None
) -> WeatherData:
    """
    Fetches real-time weather, 5-day forecast, and ET0 for a location/district in Pakistan.
    Uses geocoder if lat/lon are not explicitly provided.
    Returns typed WeatherData model with attached Evidence.
    """
    if latitude is None or longitude is None:
        geo = geocode_location(location)
        latitude = geo.latitude
        longitude = geo.longitude
        resolved_loc = f"{geo.district}, {geo.province}"
    else:
        resolved_loc = location

    client = OpenMeteoClient()
    return client.get_weather(district_or_loc=resolved_loc, lat=latitude, lon=longitude)

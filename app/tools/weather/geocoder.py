"""
Geocoding tool for Pakistani cities and agricultural districts.
"""
from datetime import datetime, timezone
from typing import Dict, Tuple, Optional
from pydantic import Field
from app.schemas.evidence import EvidentiaryDomainModel, Evidence

# Comprehensive Pakistani District & City Coordinates Registry
PAKISTANI_LOCATIONS: Dict[str, Dict[str, str | float]] = {
    "multan": {"name": "Multan", "district": "Multan", "province": "Punjab", "lat": 30.1575, "lon": 71.5249},
    "lahore": {"name": "Lahore", "district": "Lahore", "province": "Punjab", "lat": 31.5204, "lon": 74.3587},
    "faisalabad": {"name": "Faisalabad", "district": "Faisalabad", "province": "Punjab", "lat": 31.4187, "lon": 73.0791},
    "sargodha": {"name": "Sargodha", "district": "Sargodha", "province": "Punjab", "lat": 32.0836, "lon": 72.6711},
    "sahiwal": {"name": "Sahiwal", "district": "Sahiwal", "province": "Punjab", "lat": 30.6682, "lon": 73.1014},
    "bahawalpur": {"name": "Bahawalpur", "district": "Bahawalpur", "province": "Punjab", "lat": 29.3956, "lon": 71.6836},
    "rahim yar khan": {"name": "Rahim Yar Khan", "district": "Rahim Yar Khan", "province": "Punjab", "lat": 28.4212, "lon": 70.2989},
    "rawalpindi": {"name": "Rawalpindi", "district": "Rawalpindi", "province": "Punjab", "lat": 33.5651, "lon": 73.0169},
    "gujranwala": {"name": "Gujranwala", "district": "Gujranwala", "province": "Punjab", "lat": 32.1617, "lon": 74.1883},
    "sheikhupura": {"name": "Sheikhupura", "district": "Sheikhupura", "province": "Punjab", "lat": 31.7131, "lon": 73.9783},
    "okara": {"name": "Okara", "district": "Okara", "province": "Punjab", "lat": 30.8100, "lon": 73.4500},
    "pakpattan": {"name": "Pakpattan", "district": "Pakpattan", "province": "Punjab", "lat": 30.3500, "lon": 73.4000},
    "khanewal": {"name": "Khanewal", "district": "Khanewal", "province": "Punjab", "lat": 30.3000, "lon": 71.9333},
    "vehari": {"name": "Vehari", "district": "Vehari", "province": "Punjab", "lat": 30.0333, "lon": 72.3500},
    "jhang": {"name": "Jhang", "district": "Jhang", "province": "Punjab", "lat": 31.2681, "lon": 72.3181},
    "kasur": {"name": "Kasur", "district": "Kasur", "province": "Punjab", "lat": 31.1167, "lon": 74.4500},
    "sialkot": {"name": "Sialkot", "district": "Sialkot", "province": "Punjab", "lat": 32.4945, "lon": 74.5229},
    "bahawalnagar": {"name": "Bahawalnagar", "district": "Bahawalnagar", "province": "Punjab", "lat": 29.9986, "lon": 73.2536},
    "dg khan": {"name": "Dera Ghazi Khan", "district": "Dera Ghazi Khan", "province": "Punjab", "lat": 30.0561, "lon": 70.6348},
    "dera ghazi khan": {"name": "Dera Ghazi Khan", "district": "Dera Ghazi Khan", "province": "Punjab", "lat": 30.0561, "lon": 70.6348},
    "muzaffargarh": {"name": "Muzaffargarh", "district": "Muzaffargarh", "province": "Punjab", "lat": 30.0750, "lon": 71.1800},
    "layyah": {"name": "Layyah", "district": "Layyah", "province": "Punjab", "lat": 30.9600, "lon": 70.9400},
    "bhakkar": {"name": "Bhakkar", "district": "Bhakkar", "province": "Punjab", "lat": 31.6253, "lon": 71.0654},
    "miyanwali": {"name": "Mianwali", "district": "Mianwali", "province": "Punjab", "lat": 32.5853, "lon": 71.5436},
    "mianwali": {"name": "Mianwali", "district": "Mianwali", "province": "Punjab", "lat": 32.5853, "lon": 71.5436},
    "chiniot": {"name": "Chiniot", "district": "Chiniot", "province": "Punjab", "lat": 31.7200, "lon": 72.9781},
    "nankana sahib": {"name": "Nankana Sahib", "district": "Nankana Sahib", "province": "Punjab", "lat": 31.4492, "lon": 73.7124},
    "peshawar": {"name": "Peshawar", "district": "Peshawar", "province": "KPK", "lat": 34.0151, "lon": 71.5249},
    "mardan": {"name": "Mardan", "district": "Mardan", "province": "KPK", "lat": 34.1986, "lon": 72.0404},
    "swat": {"name": "Mingora", "district": "Swat", "province": "KPK", "lat": 34.7717, "lon": 72.3600},
    "sukkur": {"name": "Sukkur", "district": "Sukkur", "province": "Sindh", "lat": 27.7052, "lon": 68.8574},
    "hyderabad": {"name": "Hyderabad", "district": "Hyderabad", "province": "Sindh", "lat": 25.3960, "lon": 68.3578},
    "larkana": {"name": "Larkana", "district": "Larkana", "province": "Sindh", "lat": 27.5600, "lon": 68.2261},
    "mirpur khas": {"name": "Mirpur Khas", "district": "Mirpur Khas", "province": "Sindh", "lat": 25.5269, "lon": 69.0111},
    "nawabshah": {"name": "Nawabshah", "district": "Shaheed Benazirabad", "province": "Sindh", "lat": 26.2442, "lon": 68.4100},
    "karachi": {"name": "Karachi", "district": "Karachi", "province": "Sindh", "lat": 24.8607, "lon": 67.0011},
    "quetta": {"name": "Quetta", "district": "Quetta", "province": "Balochistan", "lat": 30.1798, "lon": 66.9750},
    "islamabad": {"name": "Islamabad", "district": "Islamabad", "province": "ICT", "lat": 33.6844, "lon": 73.0479},
}


class GeocodingResult(EvidentiaryDomainModel):
    """
    Geocoded location result for Pakistani agricultural locations.
    """
    query: str = Field(..., description="Original input location query string")
    location_name: str = Field(..., description="Resolved location/city name")
    district: str = Field(..., description="Administrative district name")
    province: str = Field(..., description="Province name")
    latitude: float = Field(...)
    longitude: float = Field(...)
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence: list[Evidence] = Field(default_factory=list)


def geocode_location(location_query: str) -> GeocodingResult:
    """
    Geocodes Pakistani city or district query into geographical coordinates.
    Returns typed GeocodingResult model with attached Evidence.
    """
    query_clean = location_query.strip().lower()
    
    # Direct match or substring match search
    matched_key = None
    for loc_key in PAKISTANI_LOCATIONS:
        if loc_key in query_clean or query_clean in loc_key:
            matched_key = loc_key
            break

    if matched_key:
        loc_info = PAKISTANI_LOCATIONS[matched_key]
        ev = Evidence(
            source_id=f"GEO_PAK_{loc_info['district'].upper().replace(' ', '_')}",
            source_name="Kisan Dost Geocoding Engine",
            verification_state="verified",
            timestamp=datetime.now(timezone.utc),
            confidence_score=0.98,
            notes=f"Resolved '{location_query}' to verified district centroid {loc_info['district']}, {loc_info['province']}."
        )
        return GeocodingResult(
            query=location_query,
            location_name=str(loc_info["name"]),
            district=str(loc_info["district"]),
            province=str(loc_info["province"]),
            latitude=float(loc_info["lat"]),
            longitude=float(loc_info["lon"]),
            confidence_score=0.98,
            evidence=[ev]
        )
    
    # Fallback to Multan (heart of Punjab agrarian belt)
    fallback_info = PAKISTANI_LOCATIONS["multan"]
    ev = Evidence(
        source_id="GEO_PAK_FALLBACK_MULTAN",
        source_name="Kisan Dost Geocoding Fallback",
        verification_state="fallback",
        timestamp=datetime.now(timezone.utc),
        confidence_score=0.65,
        notes=f"Location '{location_query}' unlisted in database. Defaulted to Multan district centroid."
    )
    return GeocodingResult(
        query=location_query,
        location_name=f"Centroid for {location_query.title()}",
        district=location_query.title(),
        province="Punjab",
        latitude=float(fallback_info["lat"]),
        longitude=float(fallback_info["lon"]),
        confidence_score=0.65,
        evidence=[ev]
    )

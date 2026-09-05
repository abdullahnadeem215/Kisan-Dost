"""
Farm Passport & Farmer Profile API endpoints.
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field
from app.schemas.farmer import FarmerProfile
from app.context.farmer_profile import FarmerProfileStore, calculate_completeness
from app.context.hydration import ContextHydrator
from config.settings import settings

router = APIRouter(prefix="/passport", tags=["Farm Passport"])

_store = FarmerProfileStore(str(settings.sqlite_db_path))


class ProfileCreateUpdateRequest(BaseModel):
    farmer_id: str = Field(..., description="Unique Farmer ID", json_schema_extra={"example": "FARM-001"})
    name: str = Field(default="Farmer", description="Farmer Name", json_schema_extra={"example": "Chaudhry Ahmad"})
    phone_number: Optional[str] = Field(None, json_schema_extra={"example": "03001234567"})
    district: str = Field(default="Multan", json_schema_extra={"example": "Multan"})
    tehsil: Optional[str] = Field(None, json_schema_extra={"example": "Multan Saddar"})
    agro_climatic_zone: str = Field(default="Cotton-Wheat Zone", json_schema_extra={"example": "Cotton-Wheat Zone"})
    total_land_acres: float = Field(default=5.0, ge=0.1, json_schema_extra={"example": 5.0})
    soil_type: str = Field(default="Loam", json_schema_extra={"example": "Loam"})
    irrigation_source: str = Field(default="Canal+Tubewell", json_schema_extra={"example": "Canal+Tubewell"})
    current_season: str = Field(default="Rabi", json_schema_extra={"example": "Rabi"})
    primary_crop: str = Field(default="Wheat", json_schema_extra={"example": "Wheat"})
    preferred_language: str = Field(default="roman_urdu", json_schema_extra={"example": "roman_urdu"})
    kisan_card_holder: bool = Field(default=True)
    max_budget_limit: Optional[float] = Field(default=250000.0)
    available_water_turns: Optional[int] = Field(default=2)


@router.get("", response_model=List[Dict[str, Any]])
async def list_farmer_passports():
    """
    Lists all registered farmer profiles with completeness metrics.
    """
    profiles = _store.list_profiles()
    if not profiles:
        default_p = ContextHydrator.get_default_profile("Multan", 5.0)
        _store.save_profile(default_p)
        profiles = [default_p]

    results = []
    for p in profiles:
        p_dict = p.model_dump()
        p_dict["completeness_percent"] = calculate_completeness(p)
        results.append(p_dict)
    return results


@router.get("/{farmer_id}", response_model=Dict[str, Any])
async def get_farmer_passport(farmer_id: str = Path(..., description="Farmer ID")):
    """
    Retrieves a farmer's persistent Farm Passport and calculated completeness score.
    """
    profile = _store.get_profile(farmer_id)
    if not profile:
        profile = ContextHydrator.get_default_profile("Multan", 5.0)
        profile.farmer_id = farmer_id

    p_dict = profile.model_dump()
    p_dict["completeness_percent"] = calculate_completeness(profile)
    return p_dict


@router.post("", response_model=Dict[str, Any])
async def save_or_update_farmer_passport(req: ProfileCreateUpdateRequest):
    """
    Creates or updates a farmer profile in the persistent SQLite passport store.
    """
    profile = FarmerProfile(
        farmer_id=req.farmer_id,
        name=req.name,
        phone_number=req.phone_number,
        district=req.district,
        tehsil=req.tehsil,
        agro_climatic_zone=req.agro_climatic_zone,
        total_land_acres=req.total_land_acres,
        soil_type=req.soil_type,
        irrigation_source=req.irrigation_source,
        current_season=req.current_season,
        primary_crop=req.primary_crop,
        preferred_language=req.preferred_language,
        kisan_card_holder=req.kisan_card_holder,
        max_budget_limit=req.max_budget_limit,
        available_water_turns=req.available_water_turns
    )
    saved = _store.save_profile(profile)
    resp = saved.model_dump()
    resp["completeness_percent"] = calculate_completeness(saved)
    return resp

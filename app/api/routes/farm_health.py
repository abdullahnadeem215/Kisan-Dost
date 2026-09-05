"""
Kisan Dost Farm Health Index API endpoints.
"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from app.services.farm_health_service import FarmHealthService

router = APIRouter(prefix="/farm-health", tags=["Farm Health Index"])


class FarmHealthCalculationRequest(BaseModel):
    farmer_id: str = Field(default="FARM-001")
    water_score: float = Field(default=62.0, ge=0.0, le=100.0, description="Water availability & irrigation score (0-100)")
    crop_condition_score: float = Field(default=84.0, ge=0.0, le=100.0, description="Crop health / vegetative vigor (0-100)")
    pest_score: float = Field(default=71.0, ge=0.0, le=100.0, description="Pest safety / bio-security score (0-100)")
    weather_score: float = Field(default=81.0, ge=0.0, le=100.0, description="Weather / climate resilience score (0-100)")
    economic_score: float = Field(default=89.0, ge=0.0, le=100.0, description="Economic margin & price outlook (0-100)")
    profile_completeness: float = Field(default=92.0, ge=0.0, le=100.0, description="Profile data completeness (0-100)")
    has_critical_data_gap: bool = Field(default=False, description="Flag if essential field data is missing")
    missing_data_reason: Optional[str] = Field(None)


@router.post("/calculate", response_model=Dict[str, Any])
async def calculate_farm_health_index(req: FarmHealthCalculationRequest):
    """
    Computes deterministic multi-factor Kisan Dost Farm Health Index (0-100) across 6 dimensions.
    If critical evidence is missing, refuses to guess and returns score_available=False.
    """
    score = FarmHealthService.calculate_farm_health(
        farmer_id=req.farmer_id,
        water_score=req.water_score,
        crop_condition_score=req.crop_condition_score,
        pest_score=req.pest_score,
        weather_score=req.weather_score,
        economic_score=req.economic_score,
        profile_completeness=req.profile_completeness,
        has_critical_data_gap=req.has_critical_data_gap,
        missing_data_reason=req.missing_data_reason
    )
    return score.model_dump()


@router.get("/{farmer_id}", response_model=Dict[str, Any])
async def get_farmer_health_index(farmer_id: str):
    """
    Retrieves baseline farm health index for a given farmer profile.
    """
    score = FarmHealthService.calculate_farm_health(
        farmer_id=farmer_id,
        water_score=62.0,
        crop_condition_score=84.0,
        pest_score=71.0,
        weather_score=81.0,
        economic_score=89.0,
        profile_completeness=92.0
    )
    return score.model_dump()

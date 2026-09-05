"""
Crop agronomy schema.
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.evidence import EvidentiaryDomainModel, Evidence


class CropStageInfo(BaseModel):
    stage_name: str
    duration_days: int
    key_tasks: List[str]


class CropInfo(EvidentiaryDomainModel):
    """
    Agronomic rules and data for a specific crop variety in Pakistan.
    """
    crop_name: str = Field(..., description="Name of crop (e.g. Wheat, Cotton)")
    variety: str = Field(..., description="Crop variety (e.g. Akbar-19, FH-142)")
    season: str = Field(..., description="Cropping season: Rabi, Kharif, Zaid")
    sowing_window: str = Field(..., description="Recommended sowing date range")
    growth_duration_days: int = Field(..., ge=1)
    water_requirement_mm: float = Field(..., ge=0.0)
    optimal_temp_min_c: float = Field(...)
    optimal_temp_max_c: float = Field(...)
    avg_yield_maunds_per_acre: float = Field(..., ge=0.0)
    potential_yield_maunds_per_acre: float = Field(..., ge=0.0)
    recommended_npk_kg_per_acre: str = Field(..., description="Recommended N-P-K in kg/acre (e.g. 50-25-15)")
    stages: List[CropStageInfo] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list, description="Agronomic source evidence")

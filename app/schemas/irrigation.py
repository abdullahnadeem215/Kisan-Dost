"""
Irrigation water management schema.
"""
from typing import Optional
from pydantic import Field
from app.schemas.evidence import EvidentiaryDomainModel, Evidence


class IrrigationSchedule(EvidentiaryDomainModel):
    """
    Irrigation schedule recommendation calculated from soil, ET0, and crop stage.
    """
    crop_name: str = Field(...)
    growth_stage: str = Field(...)
    soil_type: str = Field(..., description="Soil texture: Sandy, Loam, Clay, Clay-Loam")
    current_moisture_percent: float = Field(..., ge=0.0, le=100.0)
    daily_water_need_mm: float = Field(..., ge=0.0)
    recommended_water_depth_mm: float = Field(..., ge=0.0)
    next_irrigation_date: str = Field(..., description="Recommended date YYYY-MM-DD")
    irrigation_method: str = Field(default="Flood Irrigation", description="Flood, Drip, Sprinkler, Bed-and-Furrow")
    water_saving_tips: Optional[str] = Field(None)
    evidence: list[Evidence] = Field(default_factory=list, description="Irrigation calculation evidence")

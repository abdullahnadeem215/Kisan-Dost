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
    etc_mm_day: float = Field(default=3.5, ge=0.0, description="Crop Evapotranspiration ETc in mm/day (ET0 * Kc)")
    et0_mm_day: float = Field(default=4.5, ge=0.0, description="Reference Evapotranspiration ET0 in mm/day")
    crop_coefficient_kc: float = Field(default=0.80, ge=0.0, description="FAO-56 Crop coefficient Kc")
    explicit_assumptions: list[str] = Field(default_factory=list, description="Explicitly exposed FAO-56 Penman-Monteith methodology assumptions")
    assumptions_breakdown: dict[str, float | str] = Field(default_factory=dict, description="Structured numerical assumptions")
    evidence: list[Evidence] = Field(default_factory=list, description="Irrigation calculation evidence")

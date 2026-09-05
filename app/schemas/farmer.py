"""
Farmer profile schema.
"""
from typing import Optional
from pydantic import Field
from app.schemas.evidence import EvidentiaryDomainModel, Evidence


class FarmerProfile(EvidentiaryDomainModel):
    """
    Profile information for a registered farmer.
    """
    farmer_id: str = Field(..., description="Unique ID for the farmer")
    name: str = Field(..., description="Farmer full name")
    phone_number: Optional[str] = Field(None, description="Contact phone number")
    district: str = Field(..., description="District location (e.g. Multan, Sargodha)")
    tehsil: Optional[str] = Field(None, description="Tehsil location")
    agro_climatic_zone: str = Field(..., description="Agro-climatic zone of the farm")
    total_land_acres: float = Field(..., ge=0.0, description="Total land holding in acres")
    soil_type: str = Field(default="Loam", description="Soil type: Loam, Clay, Sandy, etc.")
    irrigation_source: str = Field(default="Canal", description="Primary water source: Canal, Tubewell, Rainfed, Mixed")
    preferred_language: str = Field(default="ur", description="Preferred interaction language: ur, en, pnb")
    kisan_card_holder: bool = Field(default=False, description="Whether farmer holds a Punjab Kisan Card")
    max_budget_limit: Optional[float] = Field(None, description="Seasonal budget limit in PKR")
    available_water_turns: Optional[int] = Field(None, description="Available water turns per month")
    evidence: list[Evidence] = Field(default_factory=list, description="Evidence items for farmer verification data")

    @property
    def land_acres(self) -> float:
        return self.total_land_acres

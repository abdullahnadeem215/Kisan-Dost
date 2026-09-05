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
    name: str = Field(default="Farmer", description="Farmer full name")
    phone_number: Optional[str] = Field(None, description="Contact phone number")
    district: str = Field(..., description="District location (e.g. Multan, Sargodha)")
    tehsil: Optional[str] = Field(None, description="Tehsil location")
    agro_climatic_zone: str = Field(default="Cotton-Wheat Zone", description="Agro-climatic zone of the farm")
    total_land_acres: float = Field(default=1.0, ge=0.0, description="Total land holding in acres")
    soil_type: str = Field(default="Loam", description="Soil type: Loam, Clay, Sandy, etc.")
    irrigation_source: str = Field(default="Canal", description="Primary water source: Canal, Tubewell, Rainfed, Mixed")
    current_season: Optional[str] = Field(default="Rabi", description="Current cropping season: Rabi or Kharif")
    primary_crop: Optional[str] = Field(default="Wheat", description="Current or planned primary crop")
    preferred_language: str = Field(default="ur", description="Preferred interaction language: ur, en, pnb, roman_urdu")
    kisan_card_holder: bool = Field(default=False, description="Whether farmer holds a Punjab Kisan Card")
    max_budget_limit: Optional[float] = Field(None, description="Seasonal budget limit in PKR")
    available_water_turns: Optional[int] = Field(None, description="Available water turns per month")
    evidence: list[Evidence] = Field(default_factory=list, description="Evidence items for farmer verification data")

    @property
    def land_acres(self) -> float:
        return self.total_land_acres

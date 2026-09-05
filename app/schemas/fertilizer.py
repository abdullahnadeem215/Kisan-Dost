"""
Fertilizer and soil nutrient schemas.
"""
from typing import Dict
from pydantic import Field
from app.schemas.evidence import EvidentiaryDomainModel, Evidence


class FertilizerInfo(EvidentiaryDomainModel):
    """
    Details of agricultural fertilizer product, NPK composition, and pricing.
    """
    fertilizer_id: str = Field(...)
    name: str = Field(..., description="Fertilizer product name (e.g. Urea, DAP, SOP)")
    nutrient_composition: Dict[str, float] = Field(
        ...,
        description="Percentage composition of nutrients e.g. {'N': 46.0} or {'N': 18.0, 'P2O5': 46.0}"
    )
    standard_bag_weight_kg: float = Field(default=50.0)
    current_price_pkr: float = Field(..., ge=0.0, description="Market price in PKR per bag")
    govt_subsidized: bool = Field(default=False)
    subsidy_pkr_per_bag: float = Field(default=0.0, ge=0.0)
    application_method: str = Field(..., description="e.g. Broadcast at sowing, Fertigation, Foliar spray")
    evidence: list[Evidence] = Field(default_factory=list, description="Fertilizer pricing and agronomic evidence")

"""
Financial economics and cost of production schema.
"""
from typing import Optional
from pydantic import Field
from app.schemas.evidence import EvidentiaryDomainModel, Evidence


class CropFinancialPlan(EvidentiaryDomainModel):
    """
    Cost of production, expected revenue, and ROI break-up per acre/farm.
    """
    crop_name: str = Field(...)
    land_acres: float = Field(..., ge=0.0)
    seed_cost_pkr: float = Field(..., ge=0.0)
    fertilizer_cost_pkr: float = Field(..., ge=0.0)
    pesticide_cost_pkr: float = Field(..., ge=0.0)
    irrigation_cost_pkr: float = Field(..., ge=0.0)
    labor_cost_pkr: float = Field(..., ge=0.0)
    machinery_cost_pkr: float = Field(..., ge=0.0)
    other_cost_pkr: float = Field(default=0.0, ge=0.0)
    total_cost_pkr: float = Field(..., ge=0.0)
    expected_yield_maunds: float = Field(..., ge=0.0)
    expected_price_pkr_per_maund: float = Field(..., ge=0.0)
    gross_revenue_pkr: float = Field(..., ge=0.0)
    net_profit_pkr: float = Field(...)
    roi_percent: float = Field(..., description="Return on investment percentage")
    evidence: list[Evidence] = Field(default_factory=list, description="Financial calculation evidence")

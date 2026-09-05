"""
Farm health index and multi-factor score schema.
Project-derived decision-support indicator (not an official government score).
"""
from typing import List, Optional
from pydantic import Field
from app.schemas.evidence import EvidentiaryDomainModel, Evidence


class FarmHealthScore(EvidentiaryDomainModel):
    """
    Composite health index evaluating water, crop condition, pest/disease, weather, economics, and profile completeness.
    Explicitly tracks score_available to prevent hallucinating scores when evidence is lacking.
    """
    farmer_id: str = Field(...)
    score_available: bool = Field(default=True, description="False if critical evidence is insufficient")
    unavailable_reason: Optional[str] = Field(None, description="Explanation when score cannot be computed safely")
    overall_health_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Kisan Dost Farm Health Index out of 100")
    
    # 6 Monitored Dimensions
    water_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Water supply & irrigation efficiency")
    crop_condition_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Crop vigor & yield health")
    pest_disease_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Pest safety / bio-security index")
    weather_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Climate & weather resilience")
    economic_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Economic margin & price outlook")
    profile_completeness_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Completeness of farm profile data")
    
    # Backwards compatibility fields
    soil_health_score: float = Field(default=75.0)
    water_efficiency_score: float = Field(default=70.0)
    pest_disease_risk_score: float = Field(default=20.0)
    financial_resilience_score: float = Field(default=65.0)
    
    status_label: str = Field(default="Unknown", description="Optimal, Good, Moderate Stress, Severe Risk, Insufficient Data")
    main_concern: str = Field(default="None", description="Primary limiting agronomic vector")
    key_vulnerabilities: List[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list, description="Farm health assessment evidence")

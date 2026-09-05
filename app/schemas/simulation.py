"""
Scenario simulation schema for What-If decisions and stress modeling.
"""
from typing import Optional, List, Dict, Any
from pydantic import Field, BaseModel
from app.schemas.evidence import EvidentiaryDomainModel, Evidence


class SimulationOption(BaseModel):
    """
    Structured outcome metrics for a specific simulated crop or management option.
    """
    crop: str = Field(..., description="Crop name")
    expected_yield: str = Field(..., description="e.g. 38.0 maunds/acre")
    expected_yield_maunds_per_acre: float = Field(..., ge=0.0)
    expected_revenue: str = Field(..., description="e.g. PKR 148,200")
    expected_revenue_pkr: float = Field(...)
    input_cost: str = Field(..., description="e.g. PKR 65,000")
    input_cost_pkr: float = Field(...)
    estimated_profit: str = Field(..., description="e.g. PKR 83,200")
    estimated_profit_pkr: float = Field(...)
    water_requirement: str = Field(..., description="e.g. 420 mm (4 irrigations)")
    water_requirement_mm: float = Field(...)
    water_risk: str = Field(default="LOW", description="LOW, MEDIUM, HIGH, CRITICAL")
    market_confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    overall_risk: str = Field(default="LOW", description="LOW, MEDIUM, HIGH, CRITICAL")
    overall_confidence: float = Field(default=0.88, ge=0.0, le=1.0)
    advantages: List[str] = Field(default_factory=list)
    disadvantages: List[str] = Field(default_factory=list)


class SimulationResult(EvidentiaryDomainModel):
    """
    Deterministic comparison result produced by Decision Simulator.
    Always explicitly marked as hypothetical scenario estimation.
    """
    simulation_id: str = Field(...)
    baseline_crop: str = Field(...)
    options: List[SimulationOption] = Field(..., description="Structured comparison options")
    recommended_option: str = Field(..., description="Option favored under farm constraints")
    recommendation_reason: str = Field(..., description="Deterministic decision rationale")
    tradeoffs: List[str] = Field(default_factory=list, description="Explicit trade-offs between options")
    assumptions: List[str] = Field(default_factory=list, description="Grounding agricultural assumptions")
    is_hypothetical: bool = Field(default=True, description="Strictly marks output as simulation, not guarantee")
    evidence: list[Evidence] = Field(default_factory=list, description="Simulation model evidence")


class SimulationScenario(EvidentiaryDomainModel):
    """
    Single crop stress simulation scenario (backwards compatible).
    """
    simulation_id: str = Field(...)
    crop_name: str = Field(...)
    baseline_yield_maunds: float = Field(..., ge=0.0)
    rainfall_variation_percent: float = Field(default=0.0)
    temp_anomaly_c: float = Field(default=0.0)
    fertilizer_reduction_percent: float = Field(default=0.0)
    projected_yield_maunds: float = Field(..., ge=0.0)
    projected_net_income_pkr: float = Field(...)
    risk_level: str = Field(default="Low", description="Low, Moderate, High, Severe")
    mitigation_strategies: List[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list, description="Simulation model evidence")

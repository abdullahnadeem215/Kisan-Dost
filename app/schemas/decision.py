"""
Agronomic decision and advisory schemas.
"""
from typing import List, Literal, Optional, Union, Dict, Any
from pydantic import Field, BaseModel
from app.schemas.evidence import EvidentiaryDomainModel, Evidence
from app.schemas.conflict import DecisionConflict


UrgencyLevel = Literal["low", "medium", "high", "critical"]


class ActionStep(BaseModel):
    """
    Individual concrete step for the farmer to execute.
    """
    step_number: int = Field(..., ge=1)
    title: str = Field(...)
    action: str = Field(...)
    timing: Optional[str] = Field(None, description="e.g. Sowing time, within 48h, etc.")
    input_required: Optional[str] = Field(None)


class RiskAssessment(BaseModel):
    """
    Structured risk evaluation from RiskService.
    """
    risk_level: str = Field(..., description="LOW, MEDIUM, HIGH, CRITICAL")
    risk_score: float = Field(..., ge=0.0, le=100.0)
    primary_risks: List[str] = Field(default_factory=list)
    mitigation_advice: List[str] = Field(default_factory=list)


class FinalDecision(BaseModel):
    """
    Authoritative final farm decision synthesized across specialists, conflicts, and evidence.
    """
    decision: str = Field(..., description="Core actionable recommendation")
    actions: List[Union[ActionStep, str]] = Field(..., description="Step-by-step action items")
    alternatives: List[str] = Field(default_factory=list, description="Alternative crops or strategies considered")
    tradeoffs: List[str] = Field(default_factory=list, description="Explicit trade-offs analyzed")
    conflicts: List[DecisionConflict] = Field(default_factory=list, description="Cross-agent conflicts resolved")
    assumptions: List[str] = Field(default_factory=list, description="Grounding agricultural assumptions")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Deterministic overall confidence")
    risk: Union[RiskAssessment, str] = Field(..., description="Risk assessment")
    evidence: List[Evidence] = Field(default_factory=list, description="Evidence trail")
    data_status: str = Field(default="LIVE", description="LIVE, CACHED, UNAVAILABLE")
    warnings: List[str] = Field(default_factory=list, description="Safety or regulatory warnings")


class AgronomicDecision(EvidentiaryDomainModel):
    """
    Actionable advisory recommendation synthesized by Kisan Dost core (backwards compatible).
    """
    decision_id: str = Field(...)
    category: str = Field(..., description="Category: Irrigation, Fertilizer, PestControl, MandiSale, GovtScheme")
    title: str = Field(..., description="Short recommendation headline")
    urgency: UrgencyLevel = Field(default="medium")
    action_steps: List[str] = Field(..., description="Step-by-step instructions for the farmer")
    rationale: str = Field(..., description="Agronomic and evidentiary reasoning behind decision")
    expected_impact: str = Field(..., description="Expected yield or financial improvement")
    evidence: list[Evidence] = Field(default_factory=list, description="Grounding evidence for this decision")

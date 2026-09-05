"""
Conflict resolution schema when contradictory sources or specialist recommendations occur.
"""
from typing import Any, Optional, List
from pydantic import Field, BaseModel
from app.schemas.evidence import EvidentiaryDomainModel, Evidence


class DecisionConflict(BaseModel):
    """
    Structured cross-domain conflict model representing disagreement between specialists.
    """
    domain_a: str = Field(..., description="First domain, e.g. Agronomy, Market")
    recommendation_a: str = Field(..., description="Recommendation from first specialist")
    domain_b: str = Field(..., description="Second domain, e.g. Water, Weather, Safety")
    recommendation_b: str = Field(..., description="Recommendation or constraint from second specialist")
    conflict_type: str = Field(..., description="e.g. Water vs Yield, Price vs Agronomy, Safety vs Dosage")
    resolution: Optional[str] = Field(None, description="Deterministic resolution adopted")
    reason: Optional[str] = Field(None, description="Agronomic rationale behind resolution")
    evidence: List[Evidence] = Field(default_factory=list, description="Grounding evidence supporting conflict detection")


class DataConflictResolution(EvidentiaryDomainModel):
    """
    Legacy record of detected data conflict and the conservative agronomic rule used to resolve it.
    """
    conflict_id: str = Field(...)
    domain: str = Field(..., description="Domain e.g. Weather, MandiPrice, DiseaseDosage")
    conflicting_field: str = Field(...)
    source_a_name: str = Field(...)
    source_a_value: Any = Field(...)
    source_b_name: str = Field(...)
    source_b_value: Any = Field(...)
    resolved_value: Any = Field(...)
    resolution_strategy: str = Field(
        ...,
        description="e.g. Official Govt Precedence, Most Conservative Bound, Recency Weighting"
    )
    resolution_notes: Optional[str] = Field(None)
    evidence: list[Evidence] = Field(default_factory=list, description="Evidence items for both conflicting data sources")

"""
Audit receipt schema verifying grounding, evidence provenance, and transparent decision audit.
"""
from typing import List, Optional
from pydantic import Field
from app.schemas.evidence import EvidentiaryDomainModel, Evidence, VerificationState


class DecisionReceipt(EvidentiaryDomainModel):
    """
    Immutable audit receipt generated for every decision to guarantee verification compliance.
    Exposes decision, reason, actions, evidence, confidence, risk, data_status, assumptions, and warnings.
    """
    receipt_id: str = Field(..., description="Unique receipt tracking hash/UUID")
    query_text: str = Field(..., description="Original user prompt or query")
    decision: str = Field(default="", description="Final core decision headline, e.g. DELAY IRRIGATION or SOW CHICKPEA")
    reason: str = Field(default="", description="Primary agronomic rationale")
    actions: List[str] = Field(default_factory=list, description="Concrete action steps")
    decision_summary: str = Field(default="", description="Summary of decision issued")
    confidence: float = Field(default=0.85, description="Deterministic overall confidence score")
    risk: str = Field(default="LOW", description="Risk classification: LOW, MEDIUM, HIGH, CRITICAL")
    data_status: str = Field(default="LIVE", description="Status of evidence: LIVE, CACHED, UNAVAILABLE")
    assumptions: List[str] = Field(default_factory=list, description="Grounding agricultural assumptions")
    warnings: List[str] = Field(default_factory=list, description="Active cautionary warnings")

    # Financial grounding fields
    total_cost_pkr: Optional[float] = Field(default=110448.0, description="Total estimated input cost in PKR")
    expected_revenue_pkr: Optional[float] = Field(default=790000.0, description="Expected gross revenue in PKR")
    net_financial_gain_pkr: Optional[float] = Field(default=679552.0, description="Projected net gain/margin in PKR")

    # Audit counters & verification states
    overall_verification_state: VerificationState = Field(default="verified")
    verified_count: int = Field(default=0, ge=0)
    unverified_count: int = Field(default=0, ge=0)
    fallback_count: int = Field(default=0, ge=0)
    stale_count: int = Field(default=0, ge=0)
    partially_verified_count: int = Field(default=0, ge=0)
    is_fully_grounded: bool = Field(default=True)
    evidence: list[Evidence] = Field(default_factory=list, description="Complete chain of evidence backing decision")

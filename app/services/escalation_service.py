"""
Escalation management service for Kisan Dost.
Handles escalation states: CLARIFICATION_REQUIRED, HUMAN_REVIEW_RECOMMENDED, UNVERIFIED, INSUFFICIENT_DATA, BLOCKED.
"""
from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from app.schemas.evidence import Evidence


EscalationState = Literal[
    "NONE",
    "CLARIFICATION_REQUIRED",
    "HUMAN_REVIEW_RECOMMENDED",
    "UNVERIFIED",
    "INSUFFICIENT_DATA",
    "BLOCKED"
]


class EscalationResult(BaseModel):
    """
    Structured outcome of an escalation check.
    """
    is_escalated: bool = Field(..., description="True if prompt or decision requires intervention")
    state: EscalationState = Field(default="NONE")
    reason: str = Field(..., description="Detailed explanation for the escalation decision")
    action_required: str = Field(..., description="Recommended follow-up action for agent or user")
    evidence: List[Evidence] = Field(default_factory=list)


class EscalationService:
    """
    Determines whether a query or agronomic decision must be escalated or blocked.
    """

    @classmethod
    def evaluate_escalation(
        cls,
        input_blocked: bool = False,
        blocked_reason: Optional[str] = None,
        has_unverified_pesticide: bool = False,
        is_missing_district_or_crop: bool = False,
        is_ambiguous: bool = False,
        confidence_score: float = 1.0,
        financial_investment_pkr: float = 0.0,
        risk_level: str = "LOW",
        evidence_items: Optional[List[Evidence]] = None
    ) -> EscalationResult:
        """
        Evaluates input/output conditions and assigns appropriate escalation state.
        Priority:
        1. BLOCKED (Security violation, medical prompt, or forbidden hazard)
        2. UNVERIFIED (Unverified pesticide dosage or unverified data evidence)
        3. INSUFFICIENT_DATA (Missing district or active crop location context)
        4. CLARIFICATION_REQUIRED (Ambiguous query or low model confidence)
        5. HUMAN_REVIEW_RECOMMENDED (Extremely high financial risk / > PKR 500k outlay or CRITICAL risk level)
        6. NONE (No escalation needed)
        """
        ev_list = evidence_items or []

        # 1. BLOCKED
        if input_blocked:
            return EscalationResult(
                is_escalated=True,
                state="BLOCKED",
                reason=blocked_reason or "Input query violated safety guardrails or topic boundary.",
                action_required="Reject query immediately and inform user of safety policy.",
                evidence=ev_list
            )

        # 2. UNVERIFIED
        if has_unverified_pesticide:
            return EscalationResult(
                is_escalated=True,
                state="UNVERIFIED",
                reason="Unverified pesticide formulation or dosage outside approved safety limits.",
                action_required="Block chemical recommendation; advise farmer to consult local extension officer.",
                evidence=ev_list
            )

        # 3. INSUFFICIENT_DATA
        if is_missing_district_or_crop:
            return EscalationResult(
                is_escalated=True,
                state="INSUFFICIENT_DATA",
                reason="Missing essential farm location (district) or target crop details.",
                action_required="Prompt user to specify district location and crop name.",
                evidence=ev_list
            )

        # 4. CLARIFICATION_REQUIRED
        if is_ambiguous or confidence_score < 0.40:
            return EscalationResult(
                is_escalated=True,
                state="CLARIFICATION_REQUIRED",
                reason=f"Ambiguous query context or low overall confidence ({confidence_score:.2f}).",
                action_required="Ask clarifying questions to narrow down agronomic intent.",
                evidence=ev_list
            )

        # 5. HUMAN_REVIEW_RECOMMENDED
        if risk_level == "CRITICAL" or financial_investment_pkr > 500000.0:
            return EscalationResult(
                is_escalated=True,
                state="HUMAN_REVIEW_RECOMMENDED",
                reason=f"High risk level ({risk_level}) or large financial capital outlay (PKR {financial_investment_pkr:,.0f}).",
                action_required="Recommend verification by a certified agronomy specialist or district extension agent.",
                evidence=ev_list
            )

        # 6. NONE
        return EscalationResult(
            is_escalated=False,
            state="NONE",
            reason="All safety, verification, and risk thresholds are satisfied.",
            action_required="Proceed with issuing automated decision advisory.",
            evidence=ev_list
        )

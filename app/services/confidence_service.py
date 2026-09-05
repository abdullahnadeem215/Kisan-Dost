"""
Confidence evaluation service separating Model Confidence, Evidence Confidence, and Overall Confidence.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.evidence import Evidence


class ConfidenceMetrics(BaseModel):
    """
    Structured confidence metrics breakdown.
    """
    model_confidence: float = Field(..., ge=0.0, le=1.0, description="Model/LLM self-assessed or inference confidence")
    evidence_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence of backing evidence items")
    overall_confidence: float = Field(..., ge=0.0, le=1.0, description="Deterministic overall confidence index")
    confidence_level: str = Field(..., description="HIGH, MEDIUM, LOW, CRITICAL")


STATE_CONFIDENCE_WEIGHTS = {
    "verified": 1.0,
    "partially_verified": 0.75,
    "cached": 0.70,
    "fallback": 0.50,
    "stale": 0.40,
    "unverified": 0.0
}


class ConfidenceService:
    """
    Evaluates multi-factor confidence across model outputs and evidence chains.
    """

    @staticmethod
    def calculate_evidence_confidence(evidence_items: List[Evidence]) -> float:
        """
        Computes weighted evidence confidence from a list of Evidence objects.
        """
        if not evidence_items:
            return 0.0

        scores = []
        for ev in evidence_items:
            base_wt = STATE_CONFIDENCE_WEIGHTS.get(ev.verification_state, 0.0)
            score = base_wt * ev.confidence_score
            scores.append(score)

        return sum(scores) / len(scores)

    @classmethod
    def evaluate_confidence(
        cls,
        model_confidence: float,
        evidence_items: List[Evidence]
    ) -> ConfidenceMetrics:
        """
        Deterministically computes overall confidence.
        Overall confidence uses a strict formula:
        overall = 0.35 * model_confidence + 0.65 * evidence_confidence
        If any evidence item is unverified or evidence list is empty, overall confidence cannot exceed 0.50.
        """
        m_conf = max(0.0, min(1.0, model_confidence))
        e_conf = cls.calculate_evidence_confidence(evidence_items)

        overall = 0.35 * m_conf + 0.65 * e_conf

        # Strict safety cap if no evidence or unverified evidence present
        has_unverified = any(ev.verification_state == "unverified" for ev in evidence_items)
        if not evidence_items or has_unverified:
            overall = min(overall, 0.45)

        overall = round(max(0.0, min(1.0, overall)), 3)

        if overall >= 0.80:
            level = "HIGH"
        elif overall >= 0.60:
            level = "MEDIUM"
        elif overall >= 0.35:
            level = "LOW"
        else:
            level = "CRITICAL"

        return ConfidenceMetrics(
            model_confidence=round(m_conf, 3),
            evidence_confidence=round(e_conf, 3),
            overall_confidence=overall,
            confidence_level=level
        )

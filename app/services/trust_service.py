"""
Trust Service evaluating evidence verification states, staleness, and provider reliability.
"""
from typing import List
from pydantic import BaseModel, Field
from app.schemas.evidence import Evidence


class TrustReport(BaseModel):
    """
    Detailed trust report evaluating evidence verification distribution and trust score.
    """
    trust_score: float = Field(..., ge=0.0, le=100.0, description="Trust score out of 100")
    live_count: int = Field(default=0, ge=0)
    cached_count: int = Field(default=0, ge=0)
    stale_count: int = Field(default=0, ge=0)
    unverified_count: int = Field(default=0, ge=0)
    fallback_count: int = Field(default=0, ge=0)
    partially_verified_count: int = Field(default=0, ge=0)
    trust_category: str = Field(..., description="FULLY_TRUSTED, PROVISIONAL, UNTRUSTED, REJECTED")
    is_trusted: bool = Field(...)

    @property
    def trust_level(self) -> str:
        return self.trust_category


class TrustService:
    """
    Evaluates evidence chains to ensure strict trust boundaries before decisions are issued.
    """

    @classmethod
    def evaluate_evidence_trust(cls, evidence_items: List[Evidence]) -> TrustReport:
        """
        Evaluates live vs cached vs stale vs unverified evidence.
        Score calculation:
        - verified: +100 pts
        - partially_verified: +75 pts
        - cached: +70 pts
        - fallback: +50 pts
        - stale: +30 pts
        - unverified: 0 pts
        """
        if not evidence_items:
            return TrustReport(
                trust_score=0.0,
                trust_category="REJECTED",
                is_trusted=False
            )

        live_cnt = 0
        cached_cnt = 0
        stale_cnt = 0
        unverified_cnt = 0
        fallback_cnt = 0
        partial_cnt = 0

        total_pts = 0.0

        for ev in evidence_items:
            st = ev.verification_state
            if st == "verified":
                live_cnt += 1
                total_pts += 100.0
            elif st == "partially_verified":
                partial_cnt += 1
                total_pts += 75.0
            elif st == "cached":
                cached_cnt += 1
                total_pts += 70.0
            elif st == "fallback":
                fallback_cnt += 1
                total_pts += 50.0
            elif st == "stale":
                stale_cnt += 1
                total_pts += 30.0
            else:  # unverified
                unverified_cnt += 1
                total_pts += 0.0

        score = total_pts / len(evidence_items)

        # Categorize
        if unverified_cnt > 0:
            category = "UNTRUSTED" if score >= 40.0 else "REJECTED"
            is_trusted = False
        elif score >= 85.0:
            category = "FULLY_TRUSTED"
            is_trusted = True
        elif score >= 60.0:
            category = "PROVISIONAL"
            is_trusted = True
        else:
            category = "UNTRUSTED"
            is_trusted = False

        return TrustReport(
            trust_score=round(score, 1),
            live_count=live_cnt,
            cached_count=cached_cnt,
            stale_count=stale_cnt,
            unverified_count=unverified_cnt,
            fallback_count=fallback_cnt,
            partially_verified_count=partial_cnt,
            trust_category=category,
            is_trusted=is_trusted
        )

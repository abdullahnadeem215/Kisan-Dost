"""
Pesticide Safety Guardrail enforcing strict dosage limits, chemical registration checks, and hazard blocking.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from app.tools.pest.dosage_checker import verify_pesticide_dosage, PesticideDosageCheckResult
from app.schemas.evidence import Evidence


# Globally Banned or Restricted Agricultural Chemicals in Pakistan
BANNED_CHEMICALS = [
    "ddt",
    "endosulfan",
    "monocrotophos",
    "paraquat",
    "methyl parathion",
    "dieldrin",
    "aldrin",
    "heptachlor",
    "chlordane"
]


class PesticideSafetyResult(BaseModel):
    """
    Result of pesticide safety audit.
    """
    is_safe: bool = Field(..., description="True if chemical and dosage are safe and verified")
    status: str = Field(..., description="VERIFIED, UNVERIFIED, or BLOCKED_HAZARD")
    crop_name: str = Field(...)
    pest_name: str = Field(...)
    active_ingredient: str = Field(...)
    proposed_dosage: float = Field(...)
    unit: str = Field(...)
    warning_messages: List[str] = Field(default_factory=list)
    actionable_recommendation: str = Field(...)
    evidence: List[Evidence] = Field(default_factory=list)


class PesticideSafetyGuardrail:
    """
    Enforces non-negotiable chemical safety, blocking unverified pesticides or lethal dosages.
    """

    @classmethod
    def audit_pesticide_recommendation(
        cls,
        crop_name: str,
        pest_name: str,
        active_ingredient: str,
        formulation: str,
        proposed_dosage: float,
        unit: str = "g"
    ) -> PesticideSafetyResult:
        """
        Audits pesticide active ingredient, formulation, and dosage against plant protection rules.
        """
        ai_clean = active_ingredient.strip().lower()

        # 1. Banned Chemical Check
        if any(banned in ai_clean for banned in BANNED_CHEMICALS):
            warning = f"BLOCKED HAZARD: '{active_ingredient}' is a banned/restricted chemical in Pakistan."
            ev = Evidence(
                source_id="BANNED_CHEMICAL_AUDIT",
                source_name="Pakistan Environmental & Plant Protection Registry",
                verification_state="unverified",
                confidence_score=0.0,
                notes=warning
            )
            return PesticideSafetyResult(
                is_safe=False,
                status="BLOCKED_HAZARD",
                crop_name=crop_name,
                pest_name=pest_name,
                active_ingredient=active_ingredient,
                proposed_dosage=proposed_dosage,
                unit=unit,
                warning_messages=[warning],
                actionable_recommendation="Do not use banned chemical. Switch to registered biopesticide or recommended IPM practice.",
                evidence=[ev]
            )

        # 2. Dosage & Registry Verification Check via dosage_checker tool
        check_result: PesticideDosageCheckResult = verify_pesticide_dosage(
            crop_name=crop_name,
            pest_name=pest_name,
            active_ingredient=active_ingredient,
            formulation=formulation,
            dosage_val=proposed_dosage,
            unit=unit
        )

        warnings = []
        if check_result.warning:
            warnings.append(check_result.warning)
        if check_result.recommendation:
            warnings.append(check_result.recommendation)

        if not check_result.is_verified:
            return PesticideSafetyResult(
                is_safe=False,
                status="UNVERIFIED",
                crop_name=crop_name,
                pest_name=pest_name,
                active_ingredient=active_ingredient,
                proposed_dosage=proposed_dosage,
                unit=unit,
                warning_messages=warnings or [f"Unverified dosage ({proposed_dosage} {unit}) or formulation ({formulation})."],
                actionable_recommendation=check_result.recommendation,
                evidence=check_result.evidence
            )

        return PesticideSafetyResult(
            is_safe=True,
            status="VERIFIED",
            crop_name=crop_name,
            pest_name=pest_name,
            active_ingredient=active_ingredient,
            proposed_dosage=proposed_dosage,
            unit=unit,
            warning_messages=[],
            actionable_recommendation=check_result.recommendation + " Wear protective gloves and mask during spray application.",
            evidence=check_result.evidence
        )

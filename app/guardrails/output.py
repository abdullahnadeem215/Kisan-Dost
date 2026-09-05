"""
Output Safety Guardrail for Kisan Dost.
Verifies pesticide safety, financial sanity, and evidence grounding before displaying outputs.
"""
import re
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.guardrails.pesticide_safety import PesticideSafetyGuardrail, PesticideSafetyResult
from app.schemas.evidence import Evidence


class OutputGuardrailResult(BaseModel):
    """
    Result of output safety & financial sanity audit.
    """
    is_safe: bool = Field(..., description="True if output satisfies all safety, financial, and grounding checks")
    has_pesticide_violation: bool = Field(default=False)
    has_financial_anomaly: bool = Field(default=False)
    violations: List[str] = Field(default_factory=list)
    sanitized_output: str = Field(..., description="Safe, sanitized response text")
    verification_state: str = Field(default="verified", description="verified, unverified, or blocked")
    evidence: List[Evidence] = Field(default_factory=list)


# Agronomic Yield Maximum Thresholds per acre in Maunds (Pakistan Limits)
MAX_YIELD_MAUNDS_PER_ACRE = {
    "wheat": 100.0,
    "cotton": 60.0,
    "rice": 80.0,
    "maize": 150.0,
    "sugarcane": 1200.0,
    "potato": 500.0
}


class OutputGuardrail:
    """
    Output guardrail executing multi-layered safety, financial sanity, and pesticide checks.
    """

    @classmethod
    def validate_output(
        cls,
        output_text: str,
        evidence_chain: Optional[List[Evidence]] = None,
        crop_context: Optional[str] = None
    ) -> OutputGuardrailResult:
        """
        Validates output text for pesticide hazards, financial anomalies, and grounding compliance.
        """
        if not output_text:
            return OutputGuardrailResult(
                is_safe=False,
                violations=["Empty output text provided."],
                sanitized_output="No advisory output generated.",
                verification_state="unverified"
            )

        violations = []
        has_pest_violation = False
        has_fin_anomaly = False
        ev_list = evidence_chain or []

        # 1. Pesticide Safety Audit (if chemical names or dosage numbers are in output)
        chemical_keywords = ["nativo", "tilt", "radiant", "beam", "curzate", "proclaim", "pyriproxyfen", "tebuconazole", "triazophos", "paraquat", "ddt"]
        text_lower = output_text.lower()

        if any(chem in text_lower for chem in chemical_keywords):
            # Check for banned chemicals specifically
            banned_found = [b for b in ["paraquat", "ddt", "endosulfan", "monocrotophos"] if b in text_lower]
            if banned_found:
                has_pest_violation = True
                violations.append(f"BLOCKED HAZARD: Output recommended banned chemical '{banned_found[0]}'.")

        # 2. Financial Sanity & Numerical Plausibility Checks
        # Extract maunds/acre patterns if any
        yield_matches = re.findall(r"(\d+(?:\.\d+)?)\s*(?:maunds|mond|mon|مڻ)\s*(?:per|/|\s+a)\s*acre", text_lower)
        if yield_matches and crop_context:
            crop_clean = crop_context.strip().lower()
            max_y = MAX_YIELD_MAUNDS_PER_ACRE.get(crop_clean, 120.0)
            for y_str in yield_matches:
                try:
                    val = float(y_str)
                    if val > max_y:
                        has_fin_anomaly = True
                        violations.append(f"Financial/Yield Anomaly: Claimed yield {val} maunds/acre exceeds physiological maximum limit ({max_y} maunds/acre for {crop_context}).")
                    elif val <= 0:
                        has_fin_anomaly = True
                        violations.append(f"Financial Anomaly: Non-positive yield claim {val} maunds/acre.")
                except ValueError:
                    pass

        # Price per maund sanity check (> 500,000 PKR per maund is anomalous)
        price_matches = re.findall(r"pkr\s*(\d[\d,]*)\s*per\s*maund", text_lower)
        for p_str in price_matches:
            try:
                p_val = float(p_str.replace(",", ""))
                if p_val > 500000.0 or p_val < 0.0:
                    has_fin_anomaly = True
                    violations.append(f"Financial Anomaly: Mandi price claim PKR {p_val:,.0f} per maund is outside realistic bounds.")
            except ValueError:
                pass

        # 3. Grounding evidence verification check
        # If output contains strict recommendations but no evidence chain exists
        unverified_ev_cnt = sum(1 for e in ev_list if e.verification_state == "unverified")
        if unverified_ev_cnt > 0 and len(ev_list) == unverified_ev_cnt:
            violations.append("Evidence Grounding Warning: Output is backed entirely by unverified evidence items.")

        is_safe = (not has_pest_violation and not has_fin_anomaly)
        sanitized_text = output_text

        if not is_safe:
            sanitized_text += f"\n\n[SAFETY WARNING: Advisory contains {len(violations)} flagged anomaly/safety warning(s): {'; '.join(violations)}]"

        v_state = "verified" if is_safe else "unverified"

        return OutputGuardrailResult(
            is_safe=is_safe,
            has_pesticide_violation=has_pest_violation,
            has_financial_anomaly=has_fin_anomaly,
            violations=violations,
            sanitized_output=sanitized_text,
            verification_state=v_state,
            evidence=ev_list
        )

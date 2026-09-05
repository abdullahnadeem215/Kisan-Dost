"""
Agronomic and Financial Risk Service for Kisan Dost.
Evaluates multi-factor risk levels: LOW, MEDIUM, HIGH, CRITICAL.
"""
from typing import List, Optional, Union
from pydantic import BaseModel, Field


class RiskAssessment(BaseModel):
    """
    Typed assessment of agronomic and financial risks.
    """
    risk_level: str = Field(..., description="LOW, MEDIUM, HIGH, CRITICAL")
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Composite risk score 0 to 100")
    agronomic_risk_score: float = Field(..., ge=0.0, le=100.0)
    financial_risk_score: float = Field(..., ge=0.0, le=100.0)
    key_risk_drivers: List[str] = Field(default_factory=list)
    mitigation_actions: List[str] = Field(default_factory=list)


class RiskService:
    """
    Evaluates multi-domain agricultural risks deterministically.
    """

    @classmethod
    def evaluate_risk(
        cls,
        water_stress: float = 0.2,
        pest_pressure: float = 0.2,
        market_volatility: float = 0.2,
        pesticide_unverified: bool = False,
        financial_vulnerability: float = 0.2
    ) -> RiskAssessment:
        """
        Computes composite risk metrics.
        - water_stress: 0.0 (no stress) to 1.0 (severe drought/canal breakdown)
        - pest_pressure: 0.0 (no pest) to 1.0 (severe outbreak)
        - market_volatility: 0.0 (stable price) to 1.0 (extreme price swings)
        - pesticide_unverified: True if pesticide dosage is unverified/unsafe
        - financial_vulnerability: 0.0 (well financed) to 1.0 (high debt)
        """
        w_stress = max(0.0, min(1.0, water_stress))
        p_pressure = max(0.0, min(1.0, pest_pressure))
        m_volatility = max(0.0, min(1.0, market_volatility))
        f_vuln = max(0.0, min(1.0, financial_vulnerability))

        drivers = []
        mitigations = []

        # Agronomic Risk Score (0-100)
        agronomic_score = (0.50 * w_stress + 0.50 * p_pressure) * 100.0
        if pesticide_unverified:
            agronomic_score = max(agronomic_score, 85.0)
            drivers.append("Unverified or unsafe pesticide formulation proposed.")
            mitigations.append("Block chemical application until verified by Plant Protection registry.")

        if w_stress >= 0.7:
            drivers.append("Severe water deficit / drought condition detected.")
            mitigations.append("Adopt drip irrigation or prioritize drought-tolerant crop variety.")
        elif w_stress >= 0.4:
            drivers.append("Moderate water stress.")
            mitigations.append("Optimize irrigation interval and alternate furrow watering.")

        if p_pressure >= 0.7:
            drivers.append("High pest outbreak intensity.")
            mitigations.append("Deploy integrated pest management (IPM) and approved bio-pesticides.")
        elif p_pressure >= 0.4:
            drivers.append("Moderate pest activity.")
            mitigations.append("Monitor pest scouting thresholds twice weekly.")

        # Financial Risk Score (0-100)
        financial_score = (0.60 * m_volatility + 0.40 * f_vuln) * 100.0
        if m_volatility >= 0.6:
            drivers.append("High market price volatility.")
            mitigations.append("Lock in floor prices or leverage Govt MSP/Passbook support.")

        if f_vuln >= 0.6:
            drivers.append("High financial vulnerability / credit constraint.")
            mitigations.append("Apply for Punjab Kisan Card interest-free credit subsidy.")

        # Composite Risk Score
        composite_score = 0.55 * agronomic_score + 0.45 * financial_score

        if pesticide_unverified or composite_score >= 75.0 or w_stress >= 0.85:
            level = "CRITICAL"
        elif composite_score >= 55.0:
            level = "HIGH"
        elif composite_score >= 30.0:
            level = "MEDIUM"
        else:
            level = "LOW"

        if not drivers:
            drivers.append("All agronomic and market risk indicators are within safe baseline bounds.")
            mitigations.append("Maintain standard recommended agronomic package of practices.")

        return RiskAssessment(
            risk_level=level,
            risk_score=round(composite_score, 1),
            agronomic_risk_score=round(agronomic_score, 1),
            financial_risk_score=round(financial_score, 1),
            key_risk_drivers=drivers,
            mitigation_actions=mitigations
        )

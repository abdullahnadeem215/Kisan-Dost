"""
Farm Health Service for computing deterministic Kisan Dost Farm Health Index (0-100).
A project-derived decision-support indicator (NOT an official government score).
"""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from app.schemas.farm_health import FarmHealthScore
from app.schemas.evidence import Evidence


class FarmHealthService:
    """
    Computes deterministic multi-factor Kisan Dost Farm Health Index.
    Evaluates 6 dimensions:
    1. Water (25%)
    2. Crop Condition (20%)
    3. Pest / Bio-security (20%)
    4. Weather Resilience (15%)
    5. Economics (10%)
    6. Profile Completeness (10%)
    """

    @classmethod
    def calculate_farm_health(
        cls,
        farmer_id: str,
        water_score: Optional[float] = 70.0,
        crop_condition_score: Optional[float] = 80.0,
        pest_score: Optional[float] = 75.0,
        weather_score: Optional[float] = 80.0,
        economic_score: Optional[float] = 85.0,
        profile_completeness: Optional[float] = 100.0,
        has_critical_data_gap: bool = False,
        missing_data_reason: Optional[str] = None,
        # Backwards compatibility parameters
        soil_health_score: Optional[float] = None,
        water_efficiency_score: Optional[float] = None,
        pest_disease_risk_score: Optional[float] = None,
        financial_resilience_score: Optional[float] = None,
        weather_risk_factor: Optional[float] = None
    ) -> FarmHealthScore:
        """
        Computes composite FarmHealthScore deterministically based on verified inputs.
        If critical evidence is missing, refuses to guess and returns score_available=False.
        """
        if has_critical_data_gap:
            return FarmHealthScore(
                farmer_id=farmer_id,
                score_available=False,
                unavailable_reason=missing_data_reason or "Insufficient agronomic evidence to safely calculate index.",
                overall_health_score=0.0,
                status_label="Insufficient Data",
                main_concern="Missing verified farm evidence",
                key_vulnerabilities=["Cannot compute index: essential field observations or profile parameters are absent."],
                evidence=[
                    Evidence(
                        source_id=f"FARM_HEALTH_GAP_{farmer_id}",
                        source_name="Kisan Dost Farm Health Engine",
                        verification_state="unverified",
                        timestamp=datetime.now(timezone.utc),
                        confidence_score=0.0,
                        notes="Refused score computation due to critical data gap."
                    )
                ]
            )

        # Handle backwards-compatible arguments if passed
        w_score = water_efficiency_score if water_efficiency_score is not None else (water_score if water_score is not None else 70.0)
        c_score = soil_health_score if soil_health_score is not None else (crop_condition_score if crop_condition_score is not None else 80.0)
        
        if pest_disease_risk_score is not None:
            p_score = max(0.0, 100.0 - pest_disease_risk_score)
        else:
            p_score = pest_score if pest_score is not None else 75.0
            
        if weather_risk_factor is not None:
            weath_score = max(0.0, 100.0 - (weather_risk_factor * 100.0))
        else:
            weath_score = weather_score if weather_score is not None else 80.0

        econ_score = financial_resilience_score if financial_resilience_score is not None else (economic_score if economic_score is not None else 85.0)
        p_comp = profile_completeness if profile_completeness is not None else 100.0

        # Bound inputs between 0 and 100
        w_val = max(0.0, min(100.0, w_score))
        c_val = max(0.0, min(100.0, c_score))
        p_val = max(0.0, min(100.0, p_score))
        weath_val = max(0.0, min(100.0, weath_score))
        e_val = max(0.0, min(100.0, econ_score))
        comp_val = max(0.0, min(100.0, p_comp))

        # Deterministic weighted formula
        overall_calc = (
            0.25 * w_val +
            0.20 * c_val +
            0.20 * p_val +
            0.15 * weath_val +
            0.10 * e_val +
            0.10 * comp_val
        )
        overall_score = round(max(0.0, min(100.0, overall_calc)), 1)

        # Status classification
        if overall_score >= 80.0:
            status_label = "Optimal"
        elif overall_score >= 65.0:
            status_label = "Good"
        elif overall_score >= 45.0:
            status_label = "Moderate Stress"
        else:
            status_label = "Severe Risk"

        # Identify main limiting concern
        dim_scores = {
            "Water availability & irrigation": w_val,
            "Crop condition & vigor": c_val,
            "Pest / Disease bio-security": p_val,
            "Weather & climate risk": weath_val,
            "Economic margin & pricing": e_val,
            "Profile data completeness": comp_val
        }
        main_concern = min(dim_scores, key=dim_scores.get)

        vulnerabilities: List[str] = []
        if w_val < 65.0:
            vulnerabilities.append(f"Water constraint: canal/tubewell deficit (Score: {w_val:.0f}/100)")
        if c_val < 65.0:
            vulnerabilities.append(f"Crop stress: low soil organic health or vegetative vigor (Score: {c_val:.0f}/100)")
        if p_val < 65.0:
            vulnerabilities.append(f"Pest vulnerability: active pest or pathogen pressure (Score: {p_val:.0f}/100)")
        if weath_val < 65.0:
            vulnerabilities.append(f"Weather shock: temperature anomaly or unseasonal rainfall (Score: {weath_val:.0f}/100)")
        if e_val < 65.0:
            vulnerabilities.append(f"Economic margin: high input costs relative to mandi price (Score: {e_val:.0f}/100)")
        if comp_val < 70.0:
            vulnerabilities.append(f"Profile completeness penalty: incomplete farm parameters ({comp_val:.0f}% complete)")

        if not vulnerabilities:
            vulnerabilities.append("All key agricultural vectors operating within healthy agronomic bounds.")

        ev = Evidence(
            source_id=f"FARM_HEALTH_{farmer_id}",
            source_name="Kisan Dost Farm Health Engine",
            verification_state="verified",
            timestamp=datetime.now(timezone.utc),
            confidence_score=round(comp_val / 100.0, 2),
            notes=f"Deterministic Kisan Dost Farm Health Index: {overall_score}/100 ({status_label}). Main concern: {main_concern}."
        )

        return FarmHealthScore(
            farmer_id=farmer_id,
            score_available=True,
            unavailable_reason=None,
            overall_health_score=overall_score,
            water_score=round(w_val, 1),
            crop_condition_score=round(c_val, 1),
            pest_disease_score=round(p_val, 1),
            weather_score=round(weath_val, 1),
            economic_score=round(e_val, 1),
            profile_completeness_score=round(comp_val, 1),
            # Backwards compatibility values
            soil_health_score=round(c_val, 1),
            water_efficiency_score=round(w_val, 1),
            pest_disease_risk_score=round(100.0 - p_val, 1),
            financial_resilience_score=round(e_val, 1),
            status_label=status_label,
            main_concern=main_concern,
            key_vulnerabilities=vulnerabilities,
            evidence=[ev]
        )

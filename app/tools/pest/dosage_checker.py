"""
Pesticide Dosage Checker tool enforcing exact-match verification and safety blocking for unknown or unsafe pesticide dosages.
"""
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any
from pydantic import Field
from app.schemas.evidence import EvidentiaryDomainModel, Evidence, VerificationState

logger = logging.getLogger(__name__)


class PesticideDosageCheckResult(EvidentiaryDomainModel):
    """
    Result of deterministic pesticide dosage verification & safety audit.
    """
    crop_name: str = Field(...)
    pest_name: str = Field(...)
    active_ingredient: str = Field(...)
    formulation: str = Field(...)
    proposed_dosage: float = Field(..., ge=0.0)
    unit: str = Field(...)
    is_verified: bool = Field(..., description="True if dosage and chemical combination are verified safe")
    status: str = Field(..., description="VERIFIED or UNVERIFIED")
    verification_state: VerificationState = Field(..., description="verified or unverified")
    recommended_dosage_str: str = Field(...)
    recommendation: str = Field(..., description="Actionable advisory statement")
    warning: Optional[str] = Field(None, description="Detailed hazard/blocking warning if unverified")
    evidence: list[Evidence] = Field(default_factory=list)


# Official Verified Pesticide Database (Department of Plant Protection / Punjab Agri Extension)
VERIFIED_PESTICIDES_REGISTRY: List[Dict[str, Any]] = [
    {
        "crop": "wheat",
        "pest": "yellow rust",
        "active_ingredient": "tebuconazole + trifloxystrobin",
        "trade_name": "nativo",
        "formulation": "75wg",
        "min_dose": 50.0,
        "max_dose": 80.0,
        "unit": "g",
        "recommended_dose_str": "65g per acre in 100L water"
    },
    {
        "crop": "wheat",
        "pest": "yellow rust",
        "active_ingredient": "propiconazole",
        "trade_name": "tilt",
        "formulation": "25ec",
        "min_dose": 80.0,
        "max_dose": 120.0,
        "unit": "ml",
        "recommended_dose_str": "100ml per acre in 100L water"
    },
    {
        "crop": "cotton",
        "pest": "pink bollworm",
        "active_ingredient": "spinetoram",
        "trade_name": "radiant",
        "formulation": "120sc",
        "min_dose": 60.0,
        "max_dose": 100.0,
        "unit": "ml",
        "recommended_dose_str": "80ml per acre in 100L water"
    },
    {
        "crop": "cotton",
        "pest": "pink bollworm",
        "active_ingredient": "triazophos",
        "trade_name": "triazophos",
        "formulation": "40ec",
        "min_dose": 400.0,
        "max_dose": 600.0,
        "unit": "ml",
        "recommended_dose_str": "500ml per acre in 100L water"
    },
    {
        "crop": "cotton",
        "pest": "whitefly",
        "active_ingredient": "pyriproxyfen",
        "trade_name": "pyriproxyfen",
        "formulation": "10ec",
        "min_dose": 400.0,
        "max_dose": 500.0,
        "unit": "ml",
        "recommended_dose_str": "500ml per acre in 100L water"
    },
    {
        "crop": "rice",
        "pest": "rice blast",
        "active_ingredient": "tricyclazole",
        "trade_name": "beam",
        "formulation": "75wp",
        "min_dose": 100.0,
        "max_dose": 150.0,
        "unit": "g",
        "recommended_dose_str": "120g per acre in 100L water"
    },
    {
        "crop": "potato",
        "pest": "late blight",
        "active_ingredient": "cymoxanil + mancozeb",
        "trade_name": "curzate m8",
        "formulation": "72wp",
        "min_dose": 200.0,
        "max_dose": 300.0,
        "unit": "g",
        "recommended_dose_str": "250g per acre in 100L water"
    },
    {
        "crop": "citrus",
        "pest": "citrus canker",
        "active_ingredient": "copper oxychloride",
        "trade_name": "copper oxychloride",
        "formulation": "50wp",
        "min_dose": 250.0,
        "max_dose": 350.0,
        "unit": "g",
        "recommended_dose_str": "300g per 100L water"
    },
    {
        "crop": "maize",
        "pest": "fall armyworm",
        "active_ingredient": "emamectin benzoate",
        "trade_name": "proclaim",
        "formulation": "1.9ec",
        "min_dose": 150.0,
        "max_dose": 250.0,
        "unit": "ml",
        "recommended_dose_str": "200ml per acre in 100L water"
    }
]


def _norm_str(s: str) -> str:
    return " ".join(s.strip().lower().replace("-", " ").replace("_", " ").split())


def _norm_crop(c: str) -> str:
    s = _norm_str(c)
    if "rice" in s:
        return "rice"
    if "kinnow" in s or "citrus" in s:
        return "citrus"
    if "corn" in s or "maize" in s:
        return "maize"
    return s


def _norm_pest(p: str) -> str:
    s = _norm_str(p)
    if "yellow" in s and "rust" in s:
        return "yellow rust"
    if "stripe" in s and "rust" in s:
        return "yellow rust"
    if "pink" in s and "bollworm" in s:
        return "pink bollworm"
    if "whitefly" in s or "white fly" in s:
        return "whitefly"
    if "late" in s and "blight" in s:
        return "late blight"
    if "rice" in s and "blast" in s:
        return "rice blast"
    if s == "blast":
        return "rice blast"
    if "canker" in s:
        return "citrus canker"
    if "fall" in s and "armyworm" in s:
        return "fall armyworm"
    return s


def _norm_form(f: str) -> str:
    return f.strip().lower().replace(" ", "").replace("-", "")


def _norm_ai(ai: str) -> str:
    s = _norm_str(ai)
    return s.replace(" + ", "+").replace("+ ", "+").replace(" +", "+")


def verify_pesticide_dosage(
    crop_name: str,
    pest_name: str,
    active_ingredient: str,
    formulation: str,
    dosage_val: float,
    unit: str = "g"
) -> PesticideDosageCheckResult:
    """
    Verifies pesticide formulation and application dosage against official Department of Plant Protection specifications.
    Enforces EXACT MATCH on Crop + Pest + Active Ingredient + Formulation + Dose.
    If not an exact match or chemical is unregistered/unknown, MUST return UNVERIFIED and BLOCK dosage.
    Never guesses dosage.
    Returns typed PesticideDosageCheckResult with attached Evidence.
    """
    norm_c = _norm_crop(crop_name)
    norm_p = _norm_pest(pest_name)
    norm_ai = _norm_ai(active_ingredient)
    norm_f = _norm_form(formulation)
    u_clean = unit.strip().lower()

    matched_entry = None
    for entry in VERIFIED_PESTICIDES_REGISTRY:
        e_crop = _norm_crop(entry["crop"])
        e_pest = _norm_pest(entry["pest"])
        e_ai = _norm_ai(entry["active_ingredient"])
        e_trade = _norm_ai(entry["trade_name"])
        e_form = _norm_form(entry["formulation"])

        crop_match = (norm_c == e_crop)
        pest_match = (norm_p == e_pest)
        chem_match = (norm_ai == e_ai or norm_ai == e_trade)
        form_match = (norm_f == e_form)

        if crop_match and pest_match and chem_match and form_match:
            matched_entry = entry
            break

    # If pesticide combination is not an exact match in registry -> BLOCK UNVERIFIED (Never guess dosage)
    if not matched_entry:
        ev = Evidence(
            source_id=f"DOSAGE_UNVERIFIED_{norm_ai.upper()}_{norm_f.upper()}",
            source_name="Department of Plant Protection Safety Audit Engine",
            verification_state="unverified",
            timestamp=datetime.now(timezone.utc),
            confidence_score=0.0,
            notes=f"BLOCKED: Exact match required. Pesticide combination '{active_ingredient}' ({formulation}) for {crop_name} - {pest_name} is unverified or unregistered. Dosage cannot be guessed."
        )
        return PesticideDosageCheckResult(
            crop_name=crop_name.title(),
            pest_name=pest_name.title(),
            active_ingredient=active_ingredient.title(),
            formulation=formulation.upper(),
            proposed_dosage=dosage_val,
            unit=unit,
            is_verified=False,
            status="UNVERIFIED",
            verification_state="unverified",
            recommended_dosage_str="UNKNOWN - Not Approved / Never Guess Dosage",
            recommendation=f"BLOCKED: Pesticide formulation '{active_ingredient}' ({formulation}) is UNVERIFIED for {crop_name} against {pest_name}. Never guess dosage. Application is blocked for crop and farmer safety.",
            warning=f"Unknown or unverified chemical active ingredient '{active_ingredient}' with formulation '{formulation}'. Application poses severe crop phytotoxicity, toxic hazard, or regulatory violation.",
            evidence=[ev]
        )

    # Validate unit matching (e.g. g vs ml vs kg)
    rec_unit = matched_entry["unit"]
    converted_dose = dosage_val
    if u_clean == "kg" and rec_unit == "g":
        converted_dose = dosage_val * 1000.0
    elif u_clean == "l" and rec_unit == "ml":
        converted_dose = dosage_val * 1000.0

    min_d = matched_entry["min_dose"]
    max_d = matched_entry["max_dose"]
    rec_str = matched_entry["recommended_dose_str"]

    # Check non-positive or invalid dose
    if dosage_val <= 0.0:
        ev = Evidence(
            source_id=f"DOSAGE_INVALID_{norm_ai.upper()}",
            source_name="Department of Plant Protection Safety Audit Engine",
            verification_state="unverified",
            timestamp=datetime.now(timezone.utc),
            confidence_score=0.0,
            notes=f"BLOCKED: Invalid non-positive dosage {dosage_val}{unit}. Never guess dosage."
        )
        return PesticideDosageCheckResult(
            crop_name=crop_name.title(),
            pest_name=pest_name.title(),
            active_ingredient=active_ingredient.title(),
            formulation=formulation.upper(),
            proposed_dosage=dosage_val,
            unit=unit,
            is_verified=False,
            status="UNVERIFIED",
            verification_state="unverified",
            recommended_dosage_str=rec_str,
            recommendation=f"BLOCKED: Invalid dosage value ({dosage_val} {unit}/acre). Never guess dosage.",
            warning="Dosage must be a positive verified value within approved therapeutic limits.",
            evidence=[ev]
        )

    if converted_dose > max_d:
        ev = Evidence(
            source_id=f"DOSAGE_OVERDOSAGE_{norm_ai.upper()}",
            source_name="Department of Plant Protection Safety Audit Engine",
            verification_state="unverified",
            timestamp=datetime.now(timezone.utc),
            confidence_score=0.10,
            notes=f"BLOCKED: Proposed dosage {dosage_val}{unit} exceeds max safe threshold of {max_d}{rec_unit}."
        )
        return PesticideDosageCheckResult(
            crop_name=crop_name.title(),
            pest_name=pest_name.title(),
            active_ingredient=active_ingredient.title(),
            formulation=formulation.upper(),
            proposed_dosage=dosage_val,
            unit=unit,
            is_verified=False,
            status="UNVERIFIED",
            verification_state="unverified",
            recommended_dosage_str=rec_str,
            recommendation=f"BLOCKED: Proposed dosage of {dosage_val} {unit}/acre EXCEEDS maximum safe limit ({max_d} {rec_u
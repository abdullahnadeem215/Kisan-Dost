"""
Pest Doctor Agent for Kisan Dost.
Equipped with function tools: disease_classifier, dosage_checker.
Enforces strict pesticide dosage verification and safety blocks.
"""
import logging
from typing import Dict, Any, Optional
from app.agents.base import Agent, function_tool
from app.tools.pest.disease_classifier import identify_disease, DiseaseDiagnosticResult
from app.tools.pest.dosage_checker import verify_pesticide_dosage, PesticideDosageCheckResult

logger = logging.getLogger(__name__)


@function_tool
def disease_classifier(
    crop_name: str = "Wheat",
    symptom_text: str = "Yellow pustules on leaves",
    image_path: Optional[str] = None
) -> DiseaseDiagnosticResult:
    """
    Identifies crop disease from symptom description or image path against verified pathology registry.
    """
    return identify_disease(
        crop_name=crop_name,
        symptom_text=symptom_text,
        image_path=image_path
    )


@function_tool
def dosage_checker(
    crop_name: str = "Wheat",
    pest_name: str = "Yellow Rust",
    active_ingredient: str = "Tebuconazole + Trifloxystrobin",
    formulation: str = "75WG",
    dosage_val: float = 65.0,
    unit: str = "g"
) -> PesticideDosageCheckResult:
    """
    Verifies pesticide formulation and application dosage against Department of Plant Protection limits.
    Blocks unverified chemicals or dosages that exceed safety limits.
    """
    return verify_pesticide_dosage(
        crop_name=crop_name,
        pest_name=pest_name,
        active_ingredient=active_ingredient,
        formulation=formulation,
        dosage_val=dosage_val,
        unit=unit
    )


PEST_DOCTOR_SYSTEM_PROMPT = """
You are the Pest Doctor Agent for Kisan Dost.
Your role is to diagnose plant diseases and audit chemical pesticide dosages for safety.
You MUST invoke disease_classifier and dosage_checker tools.
Any unverified pesticide or dangerous dosage MUST be strictly flagged and blocked.
"""

pest_doctor_agent = Agent(
    name="Pest Doctor Agent",
    instructions=PEST_DOCTOR_SYSTEM_PROMPT,
    tools=[disease_classifier, dosage_checker]
)


def run_pest_doctor_agent(query_text: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Executes Pest Doctor tools for disease diagnosis and dosage verification.
    """
    params = params or {}
    crop_name = params.get("crop_name", "Wheat")
    symptom_text = params.get("symptom_text", query_text)

    # Infer crop name if present in text
    query_lower = query_text.lower()
    for c in ["wheat", "cotton", "rice", "maize", "potato", "sugarcane", "citrus"]:
        if c in query_lower:
            crop_name = c.title()
            break

    diag = identify_disease(crop_name=crop_name, symptom_text=symptom_text)

    # Dosage check parameters
    active_ingredient = params.get("active_ingredient", "Tebuconazole + Trifloxystrobin")
    formulation = params.get("formulation", "75WG")
    dosage_val = float(params.get("dosage_val", 65.0))
    unit = params.get("unit", "g")

    dosage_res = verify_pesticide_dosage(
        crop_name=crop_name,
        pest_name=diag.disease_name,
        active_ingredient=active_ingredient,
        formulation=formulation,
        dosage_val=dosage_val,
        unit=unit
    )

    evidence_list = []
    evidence_list.extend(diag.evidence)
    evidence_list.extend(dosage_res.evidence)

    action_steps = [
        f"Diagnostic Result: {diag.disease_name} (Confidence: {diag.match_confidence*100:.0f}%).",
        f"Organic/Cultural Control: {diag.organic_control}.",
        f"Chemical Control Audit: {dosage_res.recommendation}"
    ]

    urgency = "high" if "Rust" in diag.disease_name or "Blight" in diag.disease_name else "medium"

    return {
        "agent": "Pest Doctor Agent",
        "domain": "Pest",
        "category": "Pest & Disease",
        "urgency": urgency,
        "disease_name": diag.disease_name,
        "match_confidence": diag.match_confidence,
        "dosage_check": dosage_res.model_dump(),
        "dosage_val": dosage_val,
        "max_safe_dosage": 80.0 if dosage_res.is_verified else 0.0,
        "is_verified": dosage_res.is_verified,
        "action_steps": action_steps,
        "evidence": evidence_list
    }

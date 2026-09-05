"""
Disease Classifier tool to identify plant diseases and pests from text symptoms or image model predictions.
"""
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import Field
from app.schemas.disease import DiseaseDiagnostic
from app.schemas.evidence import EvidentiaryDomainModel, Evidence
from config.settings import settings

logger = logging.getLogger(__name__)


class DiseaseDiagnosticResult(EvidentiaryDomainModel):
    """
    Diagnostic identification result containing disease details, treatment protocol, and confidence score.
    Enforces strict 0.70 confidence threshold for pathology confirmation.
    """
    crop_name: str = Field(...)
    disease_id: str = Field(...)
    disease_name: str = Field(...)
    causal_agent: str = Field(...)
    symptoms: List[str] = Field(default_factory=list)
    favorable_conditions: str = Field(...)
    preventative_measures: List[str] = Field(default_factory=list)
    organic_control: str = Field(...)
    chemical_control: str = Field(...)
    dosage_per_acre: str = Field(...)
    match_confidence: float = Field(..., ge=0.0, le=1.0)
    status: str = Field(default="CONFIRMED", description="CONFIRMED or UNCERTAIN")
    is_uncertain: bool = Field(default=False, description="True if confidence is below 0.70 safety threshold")
    candidate_distribution: List[Dict[str, Any]] = Field(default_factory=list, description="Ranked distribution of candidate disease matches")
    requires_clearer_image: bool = Field(default=False, description="True if clearer leaf image is requested")
    image_request_message: Optional[str] = Field(None, description="Guidance requesting clearer leaf photograph")
    diagnostic_summary: str = Field(...)
    evidence: list[Evidence] = Field(default_factory=list)


def identify_disease(
    crop_name: Optional[str] = None,
    symptom_text: Optional[str] = None,
    image_predictions: Optional[List[Dict[str, float | str]]] = None,
    image_path: Optional[str] = None,
    data_dir: Optional[Path] = None,
    confidence_threshold: float = 0.70
) -> DiseaseDiagnosticResult:
    """
    Identifies crop disease or pest infestation based on symptom descriptions or image classification predictions.
    Enforces model confidence threshold (default 0.70).
    If confidence < 0.70, returns UNCERTAIN with candidate distribution and requests a clearer leaf image.
    Returns typed DiseaseDiagnosticResult with attached Evidence.
    """
    base_dir = data_dir or settings.dataset_dir
    disease_file = base_dir / "diseases.json"

    diseases_db: List[Dict[str, Any]] = []
    if disease_file.exists():
        try:
            with open(disease_file, "r", encoding="utf-8") as f:
                diseases_db = json.load(f)
        except Exception as e:
            logger.error(f"Error reading diseases dataset: {e}")

    scored_candidates: List[Dict[str, Any]] = []

    # 1. Image prediction matching if provided
    if image_predictions:
        top_pred = image_predictions[0]
        label = str(top_pred.get("label", top_pred.get("class_name", ""))).lower()
        pred_conf = float(top_pred.get("confidence", 0.0))

        for item in diseases_db:
            d_name = item.get("disease_name", "").lower()
            c_name = item.get("crop_name", "").lower()
            score = 0.10

            if any(term in label for term in d_name.split()) and (not crop_name or crop_name.lower() in c_name):
                score = pred_conf
            elif c_name in label:
                score = min(0.65, pred_conf * 0.75)

            scored_candidates.append({
                "item": item,
                "score": round(score, 3),
                "notes": f"Matched via image CV classification model (Class: '{label}', Confidence: {pred_conf*100:.1f}%)."
            })

    # 2. Text symptom matching if provided
    if symptom_text:
        sym_clean = symptom_text.lower()
        sym_tokens = set(sym_clean.split())

        for item in diseases_db:
            c_name = item.get("crop_name", "").lower()
            crop_match = bool(crop_name and (crop_name.strip().lower() in c_name or c_name in crop_name.strip().lower()))

            all_text = (item.get("disease_name", "") + " " + " ".join(item.get("symptoms", []))).lower()
            item_tokens = set(all_text.split())

            overlap = len(sym_tokens.intersection(item_tokens))
            if overlap > 0:
                base_ratio = overlap / max(1, len(sym_tokens))
                calc_score = round(min(0.95, base_ratio + 0.35 if crop_match else base_ratio + 0.15), 2)
            else:
                calc_score = 0.20 if crop_match else 0.05

            scored_candidates.append({
                "item": item,
                "score": calc_score,
                "notes": f"Matched via symptom keyword analysis ('{symptom_text}')."
            })

    # Sort scored candidates descending
    scored_candidates.sort(key=lambda x: x["score"], reverse=True)

    # Build candidate distribution
    seen_ids = set()
    candidate_distribution: List[Dict[str, Any]] = []
    for cand in scored_candidates:
        cand_id = cand["item"].get("disease_id", "")
        if cand_id not in seen_ids:
            seen_ids.add(cand_id)
            candidate_distribution.append({
                "disease_name": cand["item"].get("disease_name", "Unknown"),
                "crop_name": cand["item"].get("crop_name", "General"),
                "confidence": cand["score"],
                "causal_agent": cand["item"].get("causal_agent", "Unknown")
            })
            if len(candidate_distribution) >= 5:
                break

    best_match_entry = scored_candidates[0] if scored_candidates else None
    highest_score = best_match_entry["score"] if best_match_entry else 0.0
    best_item = best_match_entry["item"] if best_match_entry else None
    matching_notes = best_match_entry["notes"] if best_match_entry else "No strong diagnostic match."

    # Emergency fallback if database empty
    if not best_item:
        best_item = {
            "disease_id": "DIS-GENERIC-UNCONFIRMED",
            "crop_name": crop_name or "General Crop",
            "disease_name": "Unconfirmed Plant Pathology",
            "causal_agent": "Unknown Pathogen",
            "symptoms": [symptom_text] if symptom_text else ["Non-specific foliar symptoms"],
            "favorable_conditions": "Humid / unventilated canopy",
            "preventative_measures": ["Field sanitation", "Avoid overhead irrigation"],
            "organic_control": "Neem oil foliar spray (5ml/L water)",
            "chemical_control": "BLOCKED: Diagnostic confidence < 0.70. Do not spray chemicals without confirmed diagnosis.",
            "dosage_per_acre": "NONE - Withheld for safety"
        }
        highest_score = 0.30
        matching_notes = "Unidentified symptom query."
        candidate_distribution = [{
            "disease_name": "Unconfirmed Plant Pathology",
            "crop_name": crop_name or "General",
            "confidence": 0.30,
            "causal_agent": "Unknown"
        }]

    # Enforce Confidence Threshold Check (< 0.70 -> UNCERTAIN)
    is_uncertain = highest_score < confidence_threshold

    if is_uncertain:
        status_str = "UNCERTAIN"
        requires_image = True
        image_request_msg = (
            "Diagnostic confidence is below 70.0% threshold. Please capture and upload a clearer, close-up photo "
            "of the affected leaf showing pustules, lesions, or margins in natural daylight before applying chemical treatments."
        )
        resolved_disease_name = f"UNCERTAIN ({best_item.get('disease_name', 'Unconfirmed')})"
        resolved_chemical = (
            "BLOCKED / WITHHELD: Model confidence is below 70.0% threshold. "
            "Never apply toxic chemical pesticides on an unconfirmed diagnosis. Upload a clearer leaf image or consult extension staff."
        )
        resolved_dosage = "NONE - Withheld until confirmed"
        diagnostic_summary = (
            f"UNCERTAIN diagnosis for {crop_name or best_item.get('crop_name')}. "
            f"Highest candidate match was '{best_item.get('disease_name')}' with only {highest_score*100:.1f}% confidence, "
            f"which is below the 70.0% threshold. Chemical spray is blocked. Clearer leaf photograph requested."
        )
        ev_state = "unverified"
        ev_notes = f"UNCERTAIN: Confidence ({highest_score*100:.1f}%) < {confidence_threshold*100:.0f}% threshold. {image_request_msg}"
    else:
        status_str = "CONFIRMED"
        requires_image = False
        image_request_msg = None
        resolved_disease_name = best_item.get("disease_name", "Unknown Disease")
        resolved_chemical = best_item.get("chemical_control", "Targeted chemical application")
        resolved_dosage = best_item.get("dosage_per_acre", "Standard recommended dose")
        diagnostic_summary = (
            f"CONFIRMED: Identified {resolved_disease_name} with {highest_score*100:.1f}% confidence "
            f"(>= {confidence_threshold*100:.0f}% safety threshold). Recommended action: {resolved_chemical}."
        )
        ev_state = "verified"
        ev_notes = f"CONFIRMED: {matching_notes} Confidence: {highest_score*100:.1f}%."

    ev = Evidence(
        source_id=f"DISEASE_ID_{best_item.get('disease_id', 'DIS')}",
        source_name="PlantVillage & Punjab Pest Warning Diagnostic Index",
        verification_state=ev_state,
        timestamp=datetime.now(timezone.utc),
        confidence_score=highest_score,
        notes=ev_notes
    )

    return DiseaseDiagnosticResult(
        crop_name=best_item.get("crop_name", crop_name or "General"),
        disease_id=best_item.get("disease_id", "DIS-UNKNOWN"),
        disease_name=resolved_disease_name,
        causal_agent=best_item.get("causal_agent", "Pest/Pathogen"),
        symptoms=best_item.get("symptoms", []),
        favorable_conditions=best_item.get("favorable_conditions", "Humid weather"),
        preventative_measures=best_item.get("preventative_measures", []),
        organic_control=best_item.get("organic_control", "Neem extract"),
        chemical_control=resolved_chemical,
        dosage_per_acre=resolved_dosage,
        match_confidence=highest_score,
        status=status_str,
        is_uncertain=is_uncertain,
        candidate_distribution=candidate_distribution,
        requires_clearer_image=requires_image,
        image_request_message=image_request_msg,
        diagnostic_summary=diagnostic_summary,
        evidence=[ev]
    )

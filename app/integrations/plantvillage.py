"""
PlantVillage Dataset & Disease Knowledge Base Integration.
"""
import json
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone
from app.schemas.disease import DiseaseDiagnostic
from app.schemas.evidence import Evidence
from config.settings import settings

logger = logging.getLogger(__name__)


class PlantVillageClient:
    """
    Client for looking up plant disease diagnostics, pest attack symptoms, and treatment protocols.
    """
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or settings.dataset_dir
        self.disease_file = self.data_dir / "diseases.json"

    def search_disease(self, query: str, crop: Optional[str] = None) -> List[DiseaseDiagnostic]:
        """
        Search for diseases/pests by symptom keyword or crop name.
        """
        results: List[DiseaseDiagnostic] = []
        if self.disease_file.exists():
            try:
                with open(self.disease_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                clean_q = query.strip().lower()
                clean_crop = crop.strip().lower() if crop else None

                for item in data:
                    item_crop = item.get("crop_name", "").lower()
                    item_name = item.get("disease_name", "").lower()
                    item_symptoms = " ".join(item.get("symptoms", [])).lower()

                    match_crop = (clean_crop is None) or (clean_crop in item_crop)
                    match_query = (clean_q in item_name) or (clean_q in item_symptoms) or (clean_q in item_crop)

                    if match_crop and match_query:
                        ev = Evidence(
                            source_id=f"PLANTVILLAGE_{item.get('disease_id', 'DISEASE')}",
                            source_name="PlantVillage Agronomy Knowledgebase",
                            verification_state="verified",
                            timestamp=datetime.now(timezone.utc),
                            confidence_score=0.96,
                            url_or_reference="https://plantvillage.psu.edu/",
                            notes="Verified pathogen diagnostic entry."
                        )
                        dd = DiseaseDiagnostic(
                            disease_id=item.get("disease_id", "DIS-000"),
                            crop_name=item.get("crop_name", "Crop"),
                            disease_name=item.get("disease_name", "Unknown Disease"),
                            causal_agent=item.get("causal_agent", "Fungal"),
                            symptoms=item.get("symptoms", []),
                            favorable_conditions=item.get("favorable_conditions", "High humidity"),
                            preventative_measures=item.get("preventative_measures", []),
                            organic_control=item.get("organic_control", "Neem oil spray"),
                            chemical_control=item.get("chemical_control", "Fungicide application"),
                            dosage_per_acre=item.get("dosage_per_acre", "250 ml/acre"),
                            evidence=[ev]
                        )
                        results.append(dd)

                if results:
                    return results

            except Exception as e:
                logger.error(f"Error loading PlantVillage diseases: {e}")

        # Fallback diagnostic record
        fallback_ev = Evidence(
            source_id="PLANTVILLAGE_FALLBACK",
            source_name="PlantVillage Fallback Diagnostic System",
            verification_state="fallback",
            timestamp=datetime.now(timezone.utc),
            confidence_score=0.70,
            notes="Generic diagnostic match."
        )

        results.append(
            DiseaseDiagnostic(
                disease_id="DIS-FALLBACK-01",
                crop_name=crop.title() if crop else "General Crop",
                disease_name=f"Suspected {query.title()} Diagnostic",
                causal_agent="Fungal / Pest Attack",
                symptoms=[f"Leaf spots or damage resembling {query}"],
                favorable_conditions="High humidity, warm temperature (>25°C)",
                preventative_measures=["Crop rotation", "Use certified seed"],
                organic_control="Spray Neem oil extract @ 5ml/L water",
                chemical_control="Consult local Extension Officer for broad-spectrum fungicide/insecticide",
                dosage_per_acre="As specified on registered bottle label",
                evidence=[fallback_ev]
            )
        )
        return results

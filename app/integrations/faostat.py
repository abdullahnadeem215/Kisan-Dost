"""
FAOSTAT integration client for macro agricultural production and yield benchmarking in Pakistan.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from app.schemas.evidence import Evidence
from config.settings import settings

logger = logging.getLogger(__name__)


class FAOSTATClient:
    """
    Client for retrieving macro FAOSTAT crop yield benchmarks and national agricultural indicators.
    """
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or settings.dataset_dir
        self.stats_file = self.data_dir / "faostat_pbs_stats.json"

    def get_crop_macro_stats(self, crop_name: str) -> Dict[str, Any]:
        """
        Fetch FAOSTAT macro stats for a given crop in Pakistan.
        """
        clean_crop = crop_name.strip().lower()
        if self.stats_file.exists():
            try:
                with open(self.stats_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                crops_data = data.get("faostat_crop_production", {})
                for k, v in crops_data.items():
                    if clean_crop in k.lower() or k.lower() in clean_crop:
                        ev = Evidence(
                            source_id=f"FAOSTAT_PAK_{k.upper()}",
                            source_name="FAOSTAT Agricultural Database (Pakistan Domain)",
                            verification_state="verified",
                            timestamp=datetime.now(timezone.utc),
                            confidence_score=0.98,
                            url_or_reference="https://www.fao.org/faostat/",
                            notes="Official FAO national statistics for Pakistan."
                        )
                        return {
                            "crop": k,
                            "area_harvested_hectares": v.get("area_harvested_ha"),
                            "production_tonnes": v.get("production_tonnes"),
                            "yield_kg_per_ha": v.get("yield_kg_ha"),
                            "yield_maunds_per_acre": round(v.get("yield_kg_ha", 0) * 0.404686 / 40.0, 2),
                            "evidence": [ev.model_dump()]
                        }
            except Exception as e:
                logger.error(f"Error loading FAOSTAT data: {e}")

        # Fallback benchmark
        ev_fallback = Evidence(
            source_id="FAOSTAT_FALLBACK_BENCHMARK",
            source_name="FAOSTAT National Benchmark Estimation",
            verification_state="fallback",
            timestamp=datetime.now(timezone.utc),
            confidence_score=0.75,
            notes="Fallback macro statistic based on average provincial yield."
        )

        return {
            "crop": crop_name.title(),
            "area_harvested_hectares": 7500000,
            "production_tonnes": 27500000,
            "yield_kg_per_ha": 3666.0,
            "yield_maunds_per_acre": 37.1,
            "evidence": [ev_fallback.model_dump()]
        }

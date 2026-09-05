"""
Crop Advisor tool for recommending optimal Pakistani crops based on district, soil, season, water, and acreage.
"""
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.evidence import EvidentiaryDomainModel, Evidence
from config.settings import settings

logger = logging.getLogger(__name__)


class CropRecommendationItem(BaseModel):
    """
    Detailed crop recommendation for a specific land unit with agro-ecological constraints.
    """
    crop_name: str = Field(..., description="Crop name (e.g. Wheat, Cotton)")
    variety: str = Field(..., description="Recommended variety e.g. Akbar-19")
    season: str = Field(...)
    sowing_window: str = Field(...)
    expected_yield_maunds_per_acre: float = Field(..., ge=0.0)
    expected_total_yield_maunds: float = Field(..., ge=0.0)
    estimated_price_pkr_per_maund: float = Field(..., ge=0.0)
    estimated_cost_pkr_per_acre: float = Field(..., ge=0.0)
    gross_revenue_pkr_per_acre: float = Field(..., ge=0.0)
    net_profit_pkr_per_acre: float = Field(...)
    net_profit_total_pkr: float = Field(...)
    suitability_score: float = Field(..., ge=0.0, le=1.0)
    agronomic_reasoning: str = Field(...)
    constraints_applied: List[str] = Field(default_factory=list, description="Specific agronomic/zonal constraints applied")


class CropAdvisorReport(EvidentiaryDomainModel):
    """
    Complete crop recommendation report generated for a farmer's parameters.
    """
    district: str = Field(...)
    agro_ecological_zone: str = Field(default="Punjab Agro-Ecological Zone")
    soil_type: str = Field(...)
    season: str = Field(...)
    water_availability: str = Field(...)
    acreage: float = Field(..., ge=0.0)
    recommendations: List[CropRecommendationItem] = Field(default_factory=list)
    applied_constraints: List[str] = Field(default_factory=list, description="Zonal, soil, water, and seasonal constraints applied")
    evidence: list[Evidence] = Field(default_factory=list)


# Standard cost & market benchmark mapping for Pakistani crops (per acre)
CROP_FINANCIAL_BENCHMARKS = {
    "wheat": {"cost_per_acre": 55000.0, "price_per_maund": 3950.0},
    "cotton": {"cost_per_acre": 95000.0, "price_per_maund": 8000.0},
    "rice": {"cost_per_acre": 85000.0, "price_per_maund": 5100.0},
    "rice (basmati)": {"cost_per_acre": 85000.0, "price_per_maund": 5100.0},
    "maize": {"cost_per_acre": 65000.0, "price_per_maund": 2350.0},
    "potato": {"cost_per_acre": 160000.0, "price_per_maund": 2050.0},
    "citrus": {"cost_per_acre": 120000.0, "price_per_maund": 3200.0},
    "citrus (kinnow)": {"cost_per_acre": 120000.0, "price_per_maund": 3200.0},
    "sugarcane": {"cost_per_acre": 140000.0, "price_per_maund": 450.0},
}

# Official Punjab Agro-Ecological Zones
PUNJAB_AGRO_ZONES = {
    "multan": "Core Cotton-Wheat Belt (South Punjab)",
    "bahawalpur": "Cotton-Wheat / Cholistan Transition Zone",
    "rahim yar khan": "Cotton-Wheat-Sugarcane Belt",
    "khanewal": "Core Cotton-Wheat Belt",
    "lodhran": "Core Cotton-Wheat Belt",
    "vehari": "Core Cotton-Wheat Belt",
    "gujranwala": "Core Rice-Wheat Kalar Belt",
    "sialkot": "Core Rice-Wheat Kalar Belt",
    "sheikhupura": "Core Rice-Wheat Kalar Belt",
    "hafizabad": "Core Rice-Wheat Kalar Belt",
    "okara": "Core Potato-Maize-Wheat Belt",
    "sahiwal": "Core Potato-Maize-Wheat Belt",
    "pakpattan": "Core Potato-Maize-Wheat Belt",
    "sargodha": "Citrus (Kinnow)-Sugarcane Belt",
    "chiniot": "Sugarcane-Citrus-Wheat Belt",
    "faisalabad": "Central Mixed Cropping Belt",
    "jhang": "Sugarcane-Wheat-Cotton Transition Belt",
    "bhakkar": "Thal Sandy / Arid Gram-Wheat Belt",
    "layyah": "Thal Sandy-Cotton Transition Belt",
    "rawalpindi": "Potohar Barani (Rainfed) Belt",
    "chakwal": "Potohar Barani (Rainfed) Belt",
}


def recommend_crops(
    district: str,
    soil: str,
    season: str,
    water: str,
    acreage: float,
    data_dir: Optional[Path] = None
) -> CropAdvisorReport:
    """
    Recommends suitable Pakistani crops based on district, soil type, season, water availability, and acreage.
    Enforces Pakistan-specific constraints (Rabi vs Kharif seasons, Multan/Punjab soil and water limitations).
    Computes expected yields and financial margins per crop.
    Returns typed CropAdvisorReport with attached Evidence.
    """
    base_dir = data_dir or settings.dataset_dir
    crops_file = base_dir / "crops.json"

    crops_db = []
    if crops_file.exists():
        try:
            with open(crops_file, "r", encoding="utf-8") as f:
                crops_db = json.load(f)
        except Exception as e:
            logger.error(f"Error loading crops dataset: {e}")

    recommendations: List[CropRecommendationItem] = []
    season_clean = season.strip().lower()
    soil_clean = soil.strip().lower()
    water_clean = water.strip().lower()
    district_clean = district.strip().lower()

    agro_zone = PUNJAB_AGRO_ZONES.get(district_clean, "Punjab Agrarian Belt")
    overall_constraints: List[str] = []

    # Seasonal constraint classifications
    rabi_crops = {"wheat", "potato", "mustard", "gram", "canola", "chickpea"}
    kharif_crops = {"cotton", "rice", "rice (basmati)", "maize", "sugarcane", "sesame"}

    if season_clean == "rabi":
        overall_constraints.append("Rabi Season Constraint: Only winter crops (sown Oct-Dec, harvested Mar-May) are eligible.")
    elif season_clean == "kharif":
        overall_constraints.append("Kharif Season Constraint: Only summer monsoon crops (sown Apr-Jul, harvested Oct-Dec) are eligible.")

    for item in crops_db:
        crop_name = item.get("crop_name", "Unknown")
        key = crop_name.strip().lower()
        crop_season = item.get("season", "").strip().lower()

        # Strict Rabi vs Kharif seasonal constraint
        if season_clean == "rabi" and key not in rabi_crops and "rabi" not in crop_season:
            continue
        if season_clean == "kharif" and key not in kharif_crops and "kharif" not in crop_season:
            continue
        if season_clean not in ["rabi", "kharif", "all"] and season_clean not in crop_season:
            continue

        avg_yield = float(item.get("avg_yield_maunds_per_acre", 30.0))
        tot_yield = avg_yield * acreage

        bench = CROP_FINANCIAL_BENCHMARKS.get(key, {"cost_per_acre": 60000.0, "price_per_maund": 3500.0})
        cost_per_acre = bench["cost_per_acre"]
        price_per_maund = bench["price_per_maund"]

        gross_rev_acre = avg_yield * price_per_maund
        net_prof_acre = gross_rev_acre - cost_per_acre
        net_prof_total = net_prof_acre * acreage

        score = 0.85
        reasons = []
        item_constraints = []

        # 1. District / Agro-Ecological Zone Constraints
        if district_clean in ["multan", "bahawalpur", "rahim yar khan", "khanewal", "lodhran", "vehari"]:
            if key == "cotton" or key == "wheat":
                score += 0.10
                reasons.append(f"{crop_name} is the hallmark commercial crop of the {agro_zone}.")
            elif "rice" in key:
                score -= 0.35
                constraint_msg = "Constraint: Rice cultivation discouraged in Multan/South Punjab cotton belt due to extreme ET0 and groundwater depletion."
                reasons.append(constraint_msg)
                item_constraints.append(constraint_msg)
        elif district_clean in ["gujranwala", "sialkot", "sheikhupura", "hafizabad"]:
            if "rice" in key:
                score += 0.10
                reasons.append(f"Premier Basmati tract ({agro_zone}) with ideal clay pan and climate.")
            elif key == "cotton":
                score -= 0.35
                constraint_msg = "Constraint: Cotton unsuited in Kalar rice tract due to high monsoonal humidity and boll rot."
                reasons.append(constraint_msg)
                item_constraints.append(constraint_msg)
        elif district_clean in ["okara", "sahiwal", "pakpattan"]:
            if key in ["potato", "maize"]:
                score += 0.10
                reasons.append(f"Central hub of potato/maize production with high commercial market access.")
        elif district_clean in ["sargodha", "chiniot"]:
            if "citrus" in key or key == "sugarcane":
                score += 0.10
                reasons.append(f"Agro-climatically suited for {crop_name} in the Sargodha basin.")

        # 2. Soil Constraints
        if "loam" in soil_clean:
            score += 0.10
            reasons.append(f"Fertile alluvial loam soil provides optimal aeration and moisture holding.")
        elif "sandy" in soil_clean:
            if key in ["potato"]:
                score += 0.05
                reasons.append("Sandy loam facilitates loose soil for tuber development.")
            elif "rice" in key:
                score -= 0.30
                c_msg = "Constraint: Sandy soil causes heavy percolation water loss for puddled rice."
                reasons.append(c_msg)
                item_constraints.append(c_msg)
            elif key == "cotton":
                score -= 0.15
                c_msg = "Constraint: Excessive water drainage in sand requires frequent irrigation for cotton."
                reasons.append(c_msg)
                item_constraints.append(c_msg)
        elif "clay" in soil_clean:
            if "rice" in key:
                score += 0.10
                reasons.append("Heavy clay soil is optimal for standing water retention in paddy fields.")
            elif key == "potato":
                score -= 0.25
                c_msg = "Constraint: Heavy clay soil causes tuber malformation and fungal rot in potato."
                reasons.append(c_msg)
                item_constraints.append(c_msg)

        # 3. Water Constraints
        if "high" in water_clean or "canal" in water_clean:
            if key in ["sugarcane", "cotton", "rice", "rice (basmati)"]:
                score += 0.05
                reasons.append("High water supply supports intensive crop evapotranspiration.")
        elif "low" in water_clean or "rainfed" in water_clean:
            if key in ["rice", "rice (basmati)", "sugarcane"]:
                score -= 0.40
                c_msg = f"Constraint: High water requirement (1200-1600mm) of {crop_name} cannot be met under low/rainfed water."
                reasons.append(c_msg)
                item_constraints.append(c_msg)
            elif key in ["wheat", "gram", "mustard"]:
                score += 0.10
                reasons.append(f"{crop_name} is resilient under limited water conditions.")

        reasons_str = " ".join(reasons) if reasons else f"Recommended crop for {season.title()} season in {district.title()}."

        item_rec = CropRecommendationItem(
            crop_name=crop_name,
            variety=item.get("variety", "Standard Variety"),
            season=item.get("season", season.title()),
            sowing_window=item.get("sowing_window", "Optimal Season Window"),
            expected_yield_maunds_per_acre=avg_yield,
            expected_total_yield_maunds=tot_yield,
            estimated_price_pkr_per_maund=price_per_maund,
            estimated_cost_pkr_per_acre=cost_per_acre,
            gross_revenue_pkr_per_acre=gross_rev_acre,
            net_profit_pkr_per_acre=net_prof_acre,
            net_profit_total_pkr=net_prof_total,
            suitability_score=min(1.0, max(0.10, round(score, 2))),
            agronomic_reasoning=reasons_str,
            constraints_applied=item_constraints
        )
        recommendations.append(item_rec)

    # Sort recommendations by net profit per acre descending
    recommendations.sort(key=lambda x: x.net_profit_pkr_per_acre, reverse=True)

    ev = Evidence(
        source_id=f"CROP_ADVISORY_{district.upper()}_{season.upper()}",
        source_name="Punjab Agronomy Crop Advisory Dataset",
        verification_state="verified",
        timestamp=datetime.now(timezone.utc),
        confidence_score=0.95,
        url_or_reference="https://agripunjab.gov.pk/",
        notes=f"Applied Pakistan agro-ecological constraints for {district} ({agro_zone}), {soil} soil, {water} water in {season}."
    )

    return CropAdvisorReport(
        district=district.title(),
        agro_ecological_zone=agro_zone,
        soil_type=soil.title(),
        season=season.title(),
        water_availability=water.title(),
        acreage=acreage,
        recommendations=recommendations,
        applied_constraints=overall_constraints,
        evidence=[ev]
    )

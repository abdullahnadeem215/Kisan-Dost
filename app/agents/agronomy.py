"""
Agronomy Agent for Kisan Dost.
Equipped with function tools: crop_advisor, fertilizer_calculator, irrigation_advisor.
"""
import logging
from typing import Dict, Any, Optional
from app.agents.base import Agent, function_tool
from app.tools.agronomy.crop_advisor import recommend_crops, CropAdvisorReport
from app.tools.agronomy.fertilizer_calculator import calculate_fertilizer_needs, FertilizerCalculationResult
from app.tools.agronomy.irrigation_advisor import compute_irrigation_schedule, IrrigationSchedule

logger = logging.getLogger(__name__)


@function_tool
def crop_advisor(
    district: str = "Multan",
    soil: str = "Loam",
    season: str = "Rabi",
    water: str = "Medium",
    acreage: float = 5.0
) -> CropAdvisorReport:
    """
    Recommends optimal Pakistani crops based on district, soil type, season, water availability, and acreage.
    """
    return recommend_crops(
        district=district,
        soil=soil,
        season=season,
        water=water,
        acreage=acreage
    )


@function_tool
def fertilizer_calculator(
    crop_name: str = "Wheat",
    acreage: float = 5.0,
    custom_npk: Optional[str] = None
) -> FertilizerCalculationResult:
    """
    Calculates NPK fertilizer requirements and commercial bag conversions (Urea, DAP, SOP) with costs in PKR.
    """
    return calculate_fertilizer_needs(
        crop_name=crop_name,
        acreage=acreage,
        custom_npk=custom_npk
    )


@function_tool
def irrigation_advisor(
    crop_name: str = "Wheat",
    growth_stage: str = "Development",
    soil_type: str = "Loam",
    et0_mm_day: float = 4.5,
    current_moisture_percent: float = 40.0,
    district: str = "Multan"
) -> IrrigationSchedule:
    """
    Computes precise evapotranspiration-based irrigation water schedules and volume requirements.
    """
    return compute_irrigation_schedule(
        crop_name=crop_name,
        growth_stage=growth_stage,
        soil_type=soil_type,
        et0_mm_day=et0_mm_day,
        current_moisture_percent=current_moisture_percent,
        district=district
    )


AGRONOMY_SYSTEM_PROMPT = """
You are the Agronomy Specialist Agent for Kisan Dost.
Your role is to advise Pakistani farmers on crop selection, NPK fertilizer dosing, and irrigation scheduling.
Always use official agronomic function tools (crop_advisor, fertilizer_calculator, irrigation_advisor) to retrieve grounded evidence.
"""

agronomy_agent = Agent(
    name="Agronomy Agent",
    instructions=AGRONOMY_SYSTEM_PROMPT,
    tools=[crop_advisor, fertilizer_calculator, irrigation_advisor]
)


def run_agronomy_agent(query_text: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Executes Agronomy Agent tools based on query context and returns structured result.
    """
    params = params or {}

    district = params.get("district", "Multan")
    crop_name = params.get("crop_name", "Wheat")
    soil = params.get("soil", "Loam")
    season = params.get("season", "Rabi")
    water = params.get("water", "Medium")
    acreage = float(params.get("acreage", 5.0))

    # Infer crop from query text if present
    query_lower = query_text.lower()
    for c in ["wheat", "cotton", "rice", "maize", "potato", "sugarcane", "citrus"]:
        if c in query_lower:
            crop_name = c.title()
            break

    # Call tools
    crop_rep = recommend_crops(district=district, soil=soil, season=season, water=water, acreage=acreage)
    fert_rep = calculate_fertilizer_needs(crop_name=crop_name, acreage=acreage)
    irri_rep = compute_irrigation_schedule(crop_name=crop_name, growth_stage="Development", soil_type=soil, et0_mm_day=4.5, current_moisture_percent=40.0, district=district)

    evidence_list = []
    evidence_list.extend(crop_rep.evidence)
    evidence_list.extend(fert_rep.evidence)
    evidence_list.extend(irri_rep.evidence)

    action_steps = [
        f"Recommended optimal crop: {crop_rep.recommendations[0].crop_name if crop_rep.recommendations else crop_name} (Expected yield: {crop_rep.recommendations[0].expected_yield_maunds_per_acre if crop_rep.recommendations else 40} maunds/acre).",
        f"Apply fertilizer package: total cost PKR {fert_rep.total_cost_pkr:,.0f} (Subsidy savings: PKR {fert_rep.subsidy_savings_pkr:,.0f}).",
        f"Irrigation schedule: {irri_rep.recommended_water_depth_mm:.1f} mm depth required ({irri_rep.water_saving_tips})."
    ]

    return {
        "agent": "Agronomy Agent",
        "domain": "Agronomy",
        "category": "Agronomy",
        "urgency": "medium",
        "crop_recommendations": [r.model_dump() for r in crop_rep.recommendations[:3]],
        "fertilizer_breakdown": fert_rep.model_dump(),
        "irrigation_schedule": irri_rep.model_dump(),
        "proposed_input_cost": fert_rep.total_cost_pkr,
        "water_required_irrigations": int(irri_rep.recommended_water_depth_mm / 25.0) if irri_rep.recommended_water_depth_mm > 0 else 1,
        "action_steps": action_steps,
        "evidence": evidence_list
    }

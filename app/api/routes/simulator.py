"""
Farm Decision Simulator (What-If Engine) API endpoints.
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.decision_simulator import DecisionSimulator
from app.schemas.simulation import SimulationResult

router = APIRouter(prefix="/simulator", tags=["Decision Simulator (What-If)"])


class CropComparisonRequest(BaseModel):
    crops: Optional[List[str]] = Field(default=["wheat", "chickpea", "canola"], description="List of crops to compare")
    land_acres: float = Field(default=5.0, ge=0.1, description="Acreage for simulation")
    water_constraint: str = Field(default="limited", description="Water condition: abundant, normal, limited, scarce")
    price_adjustments_pct: Optional[Dict[str, float]] = Field(default=None, description="Percentage adjustments to market prices, e.g. {'wheat': -10.0}")
    water_reduction_pct: float = Field(default=0.0, ge=0.0, le=100.0, description="Hypothetical water cut percentage")


class WhatIfNaturalQueryRequest(BaseModel):
    question: str = Field(..., description="Natural What-If question in English or Roman Urdu", json_schema_extra={"example": "Agar wheat ki jagah chickpea lagaoon to kya difference hoga?"})
    district: Optional[str] = Field(default="Multan")
    land_acres: Optional[float] = Field(default=5.0, ge=0.1)


@router.post("/compare", response_model=Dict[str, Any])
async def compare_crops_scenario(req: CropComparisonRequest):
    """
    Executes a deterministic multi-crop comparison exposing explicit trade-offs
    in water, input cost, expected revenue, net profit, and risk.
    """
    sim_res = DecisionSimulator.compare_multiple_crops(
        crops=req.crops,
        land_acres=req.land_acres,
        water_constraint=req.water_constraint,
        price_adjustments_pct=req.price_adjustments_pct,
        water_reduction_pct=req.water_reduction_pct
    )
    return {
        "status": "SUCCESS",
        "is_hypothetical": True,
        "simulation": sim_res.model_dump(),
        "disclaimer": "These are scenario estimates under current assumptions, not guaranteed outcomes."
    }


@router.post("/what-if", response_model=Dict[str, Any])
async def answer_what_if_question(req: WhatIfNaturalQueryRequest):
    """
    Processes a natural language What-If question, extracts parameters,
    and returns a structured simulation comparison.
    """
    profile_mock = type("MockProfile", (), {"land_acres": req.land_acres, "district": req.district})()
    res = DecisionSimulator.simulate_what_if_question(req.question, farmer_profile=profile_mock)
    
    sim_res: SimulationResult = res["simulation_result"]
    return {
        "status": "SUCCESS",
        "question": req.question,
        "is_hypothetical": True,
        "simulation": sim_res.model_dump(),
        "note": res.get("note", "SIMULATION MODE: Scenario estimate based on verified parameters.")
    }

"""
Finance & Govt Agent for Kisan Dost.
Equipped with function tools: profit_estimator, govt_support_finder.
"""
import logging
from typing import Dict, Any, Optional
from app.agents.base import Agent, function_tool
from app.tools.market.profit_estimator import estimate_crop_profit, DetailedProfitEstimate
from app.tools.govt.support_finder import find_government_support, GovtSupportReport

logger = logging.getLogger(__name__)


@function_tool
def profit_estimator(
    crop_name: str = "Wheat",
    acreage: float = 5.0,
    expected_yield_maunds_per_acre: float = 40.0,
    expected_price_pkr_per_maund: float = 4000.0,
    custom_costs_pkr_per_acre: Optional[float] = None
) -> DetailedProfitEstimate:
    """
    Calculates expected profit margins, budget requirements, and financial viability for farm operations.
    """
    return estimate_crop_profit(
        crop_name=crop_name,
        acreage=acreage,
        expected_yield_maunds_per_acre=expected_yield_maunds_per_acre,
        expected_price_pkr_per_maund=expected_price_pkr_per_maund,
        seed_cost_per_acre=custom_costs_pkr_per_acre
    )


@function_tool
def govt_support_finder(
    district: str = "Multan",
    land_acres: float = 5.0,
    crop_name: Optional[str] = None,
    interest_category: Optional[str] = None
) -> GovtSupportReport:
    """
    Identifies eligible Pakistani government agricultural subsidies, mark-up free loan schemes, and emergency relief programs.
    """
    return find_government_support(
        district=district,
        land_acres=land_acres,
        crop_name=crop_name,
        scheme_type=interest_category
    )


FINANCE_GOVT_SYSTEM_PROMPT = """
You are the Finance & Government Schemes Agent for Kisan Dost.
Your role is to evaluate farmer financial viability, credit requirements, and match farmers with active government support schemes.
Always use profit_estimator and govt_support_finder function tools for verifiable advice.
"""

finance_govt_agent = Agent(
    name="Finance & Govt Agent",
    instructions=FINANCE_GOVT_SYSTEM_PROMPT,
    tools=[profit_estimator, govt_support_finder]
)


def run_finance_govt_agent(query_text: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Executes Finance & Govt Agent tools and returns financial eligibility & subsidy report.
    """
    params = params or {}
    district = params.get("district", "Multan")
    land_acres = float(params.get("land_acres", params.get("acreage", 5.0)))
    crop_name = params.get("crop_name", "Wheat")
    expected_yield = float(params.get("expected_yield_maunds_per_acre", 40.0))
    expected_price = float(params.get("expected_price_pkr_per_maund", 4000.0))

    query_lower = query_text.lower()
    for c in ["wheat", "cotton", "rice", "maize", "potato", "sugarcane", "citrus"]:
        if c in query_lower:
            crop_name = c.title()
            break

    profit_rep = estimate_crop_profit(
        crop_name=crop_name,
        acreage=land_acres,
        expected_yield_maunds_per_acre=expected_yield,
        expected_price_pkr_per_maund=expected_price
    )
    govt_rep = find_government_support(district=district, land_acres=land_acres, crop_name=crop_name)

    evidence_list = []
    evidence_list.extend(profit_rep.evidence)
    evidence_list.extend(govt_rep.evidence)

    eligible_scheme_names = [s.scheme_name for s in govt_rep.eligible_schemes]

    action_steps = [
        f"Financial Budget: Total production cost for {land_acres} acres of {crop_name} is PKR {profit_rep.total_cost_pkr:,.0f}.",
        f"Eligible Govt Schemes: Identified {len(govt_rep.eligible_schemes)} scheme(s) including: {', '.join(eligible_scheme_names[:2])}.",
        f"Application Guidance: {govt_rep.summary}"
    ]

    return {
        "agent": "Finance & Govt Agent",
        "domain": "Finance",
        "category": "Finance & Govt Support",
        "urgency": "low",
        "profit_estimate": profit_rep.model_dump(),
        "govt_support": govt_rep.model_dump(),
        "proposed_input_cost": profit_rep.total_cost_pkr,
        "max_budget_limit": 500000.0,
        "action_steps": action_steps,
        "evidence": evidence_list
    }

"""
Market Agent for Kisan Dost.
Equipped with function tools: mandi_price_lookup, profit_estimator, selling_advisor.
"""
import logging
from typing import Dict, Any, Optional
from app.agents.base import Agent, function_tool
from app.tools.market.mandi_price import get_mandi_prices, MandiPriceReport
from app.tools.market.profit_estimator import estimate_crop_profit, DetailedProfitEstimate
from app.tools.market.selling_advisor import advise_selling_strategy, SellingAdvice

logger = logging.getLogger(__name__)


@function_tool
def mandi_price_lookup(
    commodity: str = "Wheat",
    district: str = "Multan",
    date_str: Optional[str] = None
) -> MandiPriceReport:
    """
    Fetches real-time or historical mandi market prices across Pakistani wholesale markets.
    """
    return get_mandi_prices(
        commodity=commodity,
        district=district
    )


@function_tool
def profit_estimator(
    crop_name: str = "Wheat",
    acreage: float = 5.0,
    expected_yield_maunds_per_acre: float = 40.0,
    expected_price_pkr_per_maund: float = 4000.0,
    custom_costs_pkr_per_acre: Optional[float] = None
) -> DetailedProfitEstimate:
    """
    Calculates gross revenue, total operational expenses, net profit, and break-even yields per acre.
    """
    return estimate_crop_profit(
        crop_name=crop_name,
        acreage=acreage,
        expected_yield_maunds_per_acre=expected_yield_maunds_per_acre,
        expected_price_pkr_per_maund=expected_price_pkr_per_maund,
        seed_cost_per_acre=custom_costs_pkr_per_acre
    )


@function_tool
def selling_advisor(
    crop_name: str = "Wheat",
    district: str = "Multan",
    quantity_maunds: float = 100.0,
    storage_cost_per_maund_month: float = 50.0,
    financial_urgency: str = "Medium"
) -> SellingAdvice:
    """
    Evaluates immediate mandi sale vs. post-harvest storage arbitrage opportunities.
    """
    return advise_selling_strategy(
        crop_name=crop_name,
        district=district,
        quantity_maunds=quantity_maunds,
        holding_cost_pkr_per_maund_per_month=storage_cost_per_maund_month
    )


MARKET_SYSTEM_PROMPT = """
You are the Market & Economic Advisory Agent for Kisan Dost.
Your role is to analyze mandi market trends, estimate harvest profit margins, and recommend optimal crop selling strategies.
Always ground your analysis using mandi_price_lookup, profit_estimator, and selling_advisor function tools.
"""

market_agent = Agent(
    name="Market Agent",
    instructions=MARKET_SYSTEM_PROMPT,
    tools=[mandi_price_lookup, profit_estimator, selling_advisor]
)


def run_market_agent(query_text: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Executes Market Agent tools and returns economic intelligence report.
    """
    params = params or {}
    commodity = params.get("commodity", params.get("crop_name", "Wheat"))
    district = params.get("district", "Multan")
    acreage = float(params.get("acreage", 5.0))
    quantity_maunds = float(params.get("quantity_maunds", acreage * 40.0))
    expected_yield = float(params.get("expected_yield_maunds_per_acre", 40.0))
    expected_price = float(params.get("expected_price_pkr_per_maund", 4000.0))

    query_lower = query_text.lower()
    for c in ["wheat", "cotton", "rice", "maize", "potato", "sugarcane", "citrus"]:
        if c in query_lower:
            commodity = c.title()
            break

    mandi_rep = get_mandi_prices(commodity=commodity, district=district)
    profit_rep = estimate_crop_profit(
        crop_name=commodity,
        acreage=acreage,
        expected_yield_maunds_per_acre=expected_yield,
        expected_price_pkr_per_maund=expected_price
    )
    sell_rep = advise_selling_strategy(crop_name=commodity, district=district, quantity_maunds=quantity_maunds)

    evidence_list = []
    evidence_list.extend(mandi_rep.evidence)
    evidence_list.extend(profit_rep.evidence)
    evidence_list.extend(sell_rep.evidence)

    modal_px = mandi_rep.prices[0].modal_price_pkr_per_maund if mandi_rep.prices else 4000
    action_steps = [
        f"Mandi Price Overview: Modal price in {district} is PKR {modal_px}/maund.",
        f"Profit Outlook: Net profit estimate for {acreage} acres of {commodity} is PKR {profit_rep.net_profit_pkr:,.0f} (Break-even yield: {profit_rep.break_even_yield_maunds_per_acre:.1f} maunds/acre).",
        f"Selling Strategy: {sell_rep.recommended_action} ({sell_rep.advisory_summary})."
    ]

    return {
        "agent": "Market Agent",
        "domain": "Market",
        "category": "Market & Profitability",
        "urgency": "medium",
        "mandi_prices": mandi_rep.model_dump(),
        "profit_estimate": profit_rep.model_dump(),
        "selling_advice": sell_rep.model_dump(),
        "gross_revenue": profit_rep.gross_revenue_pkr,
        "net_profit": profit_rep.net_profit_pkr,
        "action_steps": action_steps,
        "evidence": evidence_list
    }

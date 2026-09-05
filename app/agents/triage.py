"""
Triage Agent for Kisan Dost.
Analyzes farmer requests, identifies multiple intents (agronomy, pest, market, finance/govt),
and orchestrates multi-agent handoffs to specialist agents and synthesis.
"""
import logging
from typing import List, Dict, Any, Optional
from app.agents.base import Agent, Runner, RunResult, handoffs
from app.agents.agronomy import agronomy_agent
from app.agents.pest_doctor import pest_doctor_agent
from app.agents.market import market_agent
from app.agents.finance_govt import finance_govt_agent
from app.agents.synthesis import synthesis_agent
from app.schemas.farmer import FarmerProfile

logger = logging.getLogger(__name__)


def analyze_intents(query_text: str) -> List[str]:
    """
    Analyzes farmer query text to detect intent domains: agronomy, pest, market, finance_govt.
    Supports multi-intent requests.
    """
    text_lower = query_text.lower()
    intents = set()

    # Agronomy intent keywords
    agronomy_keywords = ["crop", "sow", "variety", "fertilizer", "urea", "dap", "water", "irrigation", "soil", "acre", "yield"]
    if any(k in text_lower for k in agronomy_keywords):
        intents.add("agronomy")

    # Pest Doctor intent keywords
    pest_keywords = ["pest", "disease", "rust", "blight", "yellow", "pustule", "fungus", "insect", "spray", "pesticide", "dosage", "chemical", "nativo", "tilt"]
    if any(k in text_lower for k in pest_keywords):
        intents.add("pest")

    # Market intent keywords
    market_keywords = ["mandi", "price", "rate", "profit", "sell", "selling", "store", "storage", "market", "bazaar", "revenue"]
    if any(k in text_lower for k in market_keywords):
        intents.add("market")

    # Finance & Govt intent keywords
    finance_keywords = ["scheme", "govt", "government", "subsidy", "loan", "kisan card", "support", "grant", "budget", "finance", "credit"]
    if any(k in text_lower for k in finance_keywords):
        intents.add("finance_govt")

    # If no intent matched, default to agronomy
    if not intents:
        intents.add("agronomy")

    return sorted(list(intents))


TRIAGE_SYSTEM_PROMPT = """
You are the Master Triage Agent for Kisan Dost.
Your job is to analyze multi-intent Pakistani farmer queries, route requests to appropriate specialist agents
(Agronomy, Pest Doctor, Market, Finance & Govt), and initiate handoffs to produce a synthesized agronomic advisory.
"""

triage_agent = Agent(
    name="Triage Agent",
    instructions=TRIAGE_SYSTEM_PROMPT,
    handoffs=handoffs(agronomy_agent, pest_doctor_agent, market_agent, finance_govt_agent, synthesis_agent)
)


def run_triage_pipeline(
    query_text: str,
    farmer_profile: Optional[FarmerProfile] = None,
    context: Optional[Dict[str, Any]] = None
) -> RunResult:
    """
    Initiates multi-agent workflow starting from Triage Agent, handing off to specialists,
    and synthesizing results.
    """
    ctx = context or {}
    if farmer_profile:
        ctx["farmer_profile"] = farmer_profile

    return Runner.run(
        agent=triage_agent,
        input_text=query_text,
        context=ctx
    )

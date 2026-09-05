"""
Comprehensive test suite for OpenAI Agents SDK Multi-Agent Handoff network in Kisan Dost.
"""
import pytest
from app.agents import (
    Agent,
    Runner,
    FunctionTool,
    function_tool,
    Handoff,
    handoffs,
    RunResult,
    triage_agent,
    agronomy_agent,
    pest_doctor_agent,
    market_agent,
    finance_govt_agent,
    synthesis_agent,
    run_triage_pipeline,
    analyze_intents,
    run_agronomy_agent,
    run_pest_doctor_agent,
    run_market_agent,
    run_finance_govt_agent,
    run_synthesis_agent
)
from app.schemas.farmer import FarmerProfile
from app.schemas.decision import AgronomicDecision
from app.schemas.decision_receipt import DecisionReceipt


def test_sdk_primitives():
    """Verify Agent, FunctionTool, Handoff primitives instantiation."""
    @function_tool
    def dummy_tool(x: int) -> int:
        """Dummy docstring."""
        return x * 2

    assert isinstance(dummy_tool, FunctionTool)
    assert dummy_tool(5) == 10

    test_agent = Agent(
        name="Test Agent",
        instructions="Test instructions",
        tools=[dummy_tool]
    )

    assert test_agent.name == "Test Agent"
    assert len(test_agent.tools) == 1
    assert test_agent.get_tool("dummy_tool") is not None


def test_triage_intent_analysis():
    """Verify intent analysis for multi-intent requests."""
    intents = analyze_intents("I need wheat fertilizer recommendation, mandi prices in Multan, and government subsidy information.")
    assert "agronomy" in intents
    assert "market" in intents
    assert "finance_govt" in intents

    pest_intents = analyze_intents("My wheat leaves have yellow pustules. What spray should I use?")
    assert "pest" in pest_intents or "agronomy" in pest_intents


def test_agronomy_agent_execution():
    """Verify Agronomy Agent execution and tool calls."""
    res = run_agronomy_agent("Recommend crops for Multan in Rabi season with 10 acres loam soil.")
    assert res["agent"] == "Agronomy Agent"
    assert res["domain"] == "Agronomy"
    assert len(res["crop_recommendations"]) > 0
    assert res["proposed_input_cost"] > 0
    assert len(res["evidence"]) > 0


def test_pest_doctor_agent_execution():
    """Verify Pest Doctor Agent execution and dosage audit."""
    res = run_pest_doctor_agent("Yellow pustules on wheat leaves", params={"crop_name": "Wheat", "active_ingredient": "Tebuconazole + Trifloxystrobin", "formulation": "75WG", "dosage_val": 65.0})
    assert res["agent"] == "Pest Doctor Agent"
    assert "Yellow" in res["disease_name"] or res["match_confidence"] > 0.3
    assert res["is_verified"] is True
    assert len(res["evidence"]) > 0


def test_market_agent_execution():
    """Verify Market Agent execution and economic intelligence."""
    res = run_market_agent("What is the mandi price of Wheat in Multan and should I sell now?")
    assert res["agent"] == "Market Agent"
    assert res["domain"] == "Market"
    assert res["gross_revenue"] > 0
    assert res["net_profit"] > 0
    assert len(res["evidence"]) > 0


def test_finance_govt_agent_execution():
    """Verify Finance & Govt Agent execution and scheme matching."""
    res = run_finance_govt_agent("I have 5 acres of wheat in Multan. What government support schemes am I eligible for?")
    assert res["agent"] == "Finance & Govt Agent"
    assert res["domain"] == "Finance"
    assert "govt_support" in res
    assert len(res["evidence"]) > 0


def test_synthesis_agent_execution():
    """Verify Synthesis Agent combining specialist outputs into Decision & Receipt."""
    agri_out = run_agronomy_agent("Wheat fertilizer for 5 acres")
    pest_out = run_pest_doctor_agent("Yellow rust on wheat")

    synth_res = run_synthesis_agent(
        query_text="Wheat advisor with pest audit",
        specialist_outputs=[agri_out, pest_out]
    )

    assert synth_res["agent"] == "Synthesis Agent"
    assert isinstance(synth_res["decision"], AgronomicDecision)
    assert isinstance(synth_res["receipt"], DecisionReceipt)
    assert "Kisan Dost" in synth_res["markdown"]


def test_multi_agent_triage_pipeline():
    """Verify full multi-agent handoff pipeline from Triage to Specialists to Synthesis."""
    profile = FarmerProfile(
        farmer_id="FARM-101",
        name="Muhammad Ahmad",
        district="Multan",
        agro_climatic_zone="Cotton-Wheat Zone (South Punjab)",
        total_land_acres=10.0,
        irrigation_source="Canal"
    )

    query = "I have 10 acres of wheat in Multan. Leaves have yellow pustules. Need fertilizer guide, mandi rates, and subsidy info."

    run_result = run_triage_pipeline(query_text=query, farmer_profile=profile)

    assert isinstance(run_result, RunResult)
    assert "Triage Agent" in run_result.agent_history
    assert "Synthesis Agent" in run_result.agent_history
    assert len(run_result.specialist_outputs) >= 2
    assert run_result.decision is not None
    assert run_result.receipt is not None
    assert len(run_result.evidence) > 0
    assert "Kisan Dost" in run_result.final_output
    assert "Multi-Domain Risk Warnings" in run_result.final_output

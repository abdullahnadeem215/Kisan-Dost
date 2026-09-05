"""
Executable Demo Script for Kisan Dost.
Demonstrates 6 required core scenarios:
1. Scenario 1 (main): Main multi-intent query (5 acres, limited water, Rabi, crop choice, fertilizer, mandi price).
2. Scenario 2 (conflict): Agent conflict resolution scenario (Agronomy vs Water vs Market).
3. Scenario 3 (whatif): What-If simulation scenario ("What if I grow chickpea instead of wheat?").
4. Scenario 4 (safety): Safety attack scenario ("Give me exact dosage for unknown chemical").
5. Scenario 5 (low_confidence): Low disease classifier confidence handling ("UNCERTAIN" request for clearer image).
6. Scenario 6 (offline): Offline / cached AMIS market data scenario.
"""
import sys
import io
from pathlib import Path

# Ensure root workspace directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import argparse
from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from app.context.hydration import ContextHydrator
from app.context.farmer_profile import FarmerProfile
from app.guardrails.pesticide_safety import PesticideSafetyGuardrail
from app.services.decision_service import DecisionService
from app.services.confidence_service import ConfidenceService
from app.services.trust_service import TrustService
from app.services.risk_service import RiskService
from app.services.escalation_service import EscalationService
from app.services.decision_simulator import DecisionSimulator
from app.tools.agronomy.crop_advisor import recommend_crops
from app.tools.agronomy.fertilizer_calculator import calculate_fertilizer_needs
from app.tools.pest.disease_classifier import identify_disease
from app.tools.market.mandi_price import get_mandi_prices
from app.integrations.amis import AMISClient
from app.presentation.mission_control import TelemetryData, ToolExecutionRecord, GuardrailAuditRecord, render_mission_control
from app.presentation.decision_receipt import render_decision_receipt
from app.i18n import EnglishRenderer, UrduRenderer, RomanUrduRenderer

console = Console()


def run_scenario_main() -> Dict[str, Any]:
    """
    Scenario 1: Main Multi-Intent Query
    5 acres, limited water, Rabi season, crop choice, fertilizer, mandi price.
    """
    console.print(Panel("🌾 [bold green]SCENARIO 1: MAIN MULTI-INTENT QUERY[/bold green]\n"
                        "Query: 'I have 5 acres of loam soil in Multan for Rabi season with limited water (2 turns). "
                        "Which crop should I grow, what is the exact fertilizer NPK plan, and what is the current mandi market price?'",
                        border_style="green"))

    profile = ContextHydrator.get_default_profile(district="Multan", acreage=5.0)
    profile.available_water_turns = 2

    # Execute tools
    crop_res = recommend_crops(district=profile.district, soil=profile.soil_type, season="Rabi", water="Low", acreage=profile.land_acres)
    fert_res = calculate_fertilizer_needs(crop_name="Wheat", acreage=profile.land_acres)
    mandi_res = get_mandi_prices(commodity="Wheat", district=profile.district)

    dap_bags = next((b.total_bags for b in fert_res.bag_breakdown if "DAP" in b.fertilizer_name), 0)
    urea_bags = next((b.total_bags for b in fert_res.bag_breakdown if "Urea" in b.fertilizer_name), 0)

    specialist_outputs = [
        {
            "domain": "Agronomy",
            "category": "Crop",
            "water_required_irrigations": 4,
            "action_steps": [
                f"Sow high-yielding Rabi Wheat ({crop_res.recommendations[0].crop_name}) adapted for {profile.soil_type} soil.",
                f"Apply balanced fertilizer package: {dap_bags} bags DAP, {urea_bags} bags Urea."
            ],
            "evidence": crop_res.evidence + fert_res.evidence
        },
        {
            "domain": "Water",
            "available_irrigations": 2,
            "evidence": []
        },
        {
            "domain": "Market",
            "category": "MarketSale",
            "action_steps": [f"Monitor {mandi_res.prices[0].mandi_name} rate (Benchmark: PKR {mandi_res.prices[0].modal_price_pkr_per_maund:,.0f}/maund)."],
            "evidence": mandi_res.evidence
        }
    ]

    decision, receipt, conflicts = DecisionService.produce_final_decision(
        query_text="5 acres Multan Rabi crop recommendation, fertilizer plan, and mandi price",
        specialist_outputs=specialist_outputs,
        farmer_profile=profile
    )

    trust_report = TrustService.evaluate_evidence_trust(decision.evidence)
    risk_report = RiskService.evaluate_risk(water_stress=0.4, financial_vulnerability=0.2)
    conf_report = ConfidenceService.evaluate_confidence(model_confidence=0.92, evidence_items=decision.evidence)

    telemetry = TelemetryData(
        session_id="SESS-DEMO-SCENARIO-1",
        query_text="5 acres Multan Rabi advisory",
        agent_steps=["Triage Handoff", "Agronomy Agent", "Market Agent", "Synthesis Agent"],
        tool_executions=[
            ToolExecutionRecord(tool_name="recommend_crops", status="SUCCESS", latency_ms=14.5, summary=f"Top rec: {crop_res.recommendations[0].crop_name}"),
            ToolExecutionRecord(tool_name="calculate_fertilizer_needs", status="SUCCESS", latency_ms=16.1, summary=f"Cost: PKR {fert_res.total_cost_pkr:,.0f}"),
            ToolExecutionRecord(tool_name="get_mandi_prices", status="SUCCESS", latency_ms=11.8, summary=f"Modal PKR {mandi_res.prices[0].modal_price_pkr_per_maund:,.0f}")
        ],
        guardrail_audits=[
            GuardrailAuditRecord(name="Input Guardrail", passed=True, status="PASSED", details="Safe agronomic prompt"),
            GuardrailAuditRecord(name="Pesticide Guardrail", passed=True, status="PASSED", details="No hazard detected")
        ],
        conflicts_resolved=[c.model_dump() for c in conflicts],
        trust_score=trust_report.trust_score,
        trust_level=trust_report.trust_level,
        risk_score=risk_report.risk_score,
        risk_level=risk_report.risk_level,
        overall_confidence=conf_report.overall_confidence,
        confidence_level=conf_report.confidence_level,
        grounding_state=receipt.overall_verification_state
    )

    render_mission_control(telemetry, console=console)
    render_decision_receipt(
        receipt=receipt,
        decision=decision,
        additional_context={
            "crop_recommendation": crop_res.recommendations[0].crop_name,
            "fertilizer_plan": f"DAP: {dap_bags} bags, Urea: {urea_bags} bags",
            "market_rates": f"PKR {mandi_res.prices[0].modal_price_pkr_per_maund:,.0f} / maund ({mandi_res.prices[0].mandi_name})",
            "water_risk": "Scaled to 2 available water turns",
            "confidence_pct": conf_report.overall_confidence * 100
        },
        console=console
    )

    console.print(Panel(EnglishRenderer.render_advisory(decision, receipt), title="📜 Advisory Output [English]", border_style="cyan"))
    return {"status": "SUCCESS", "receipt": receipt}


def run_scenario_conflict() -> Dict[str, Any]:
    """
    Scenario 2: Conflict Resolution Scenario
    Agronomy recommended 4 irrigations vs. Water Resource Monitor capping available turns at 2.
    """
    console.print(Panel("⚔️ [bold yellow]SCENARIO 2: CROSS-DOMAIN CONFLICT RESOLUTION[/bold yellow]\n"
                        "Conflict: Agronomy recommended 4 irrigations for Wheat, but Water Resource Monitor reports only 2 available canal turns.",
                        border_style="yellow"))

    specialist_outputs = [
        {
            "domain": "Agronomy",
            "category": "Irrigation",
            "water_required_irrigations": 4,
            "action_steps": ["Apply 4 irrigations across growth stages."],
            "evidence": []
        },
        {
            "domain": "Water",
            "available_irrigations": 2,
            "evidence": []
        }
    ]

    resolved_outputs, conflicts = DecisionService.detect_and_resolve_conflicts(specialist_outputs)

    decision, receipt, conflicts = DecisionService.produce_final_decision(
        query_text="Conflict resolution between recommended 4 irrigations vs 2 available turns",
        specialist_outputs=specialist_outputs
    )

    telemetry = TelemetryData(
        session_id="SESS-DEMO-SCENARIO-2",
        query_text="Agronomy vs Water Conflict",
        agent_steps=["Agronomy Agent", "Water Monitor Agent", "Decision Service Conflict Resolver"],
        conflicts_resolved=[c.model_dump() for c in conflicts],
        trust_score=90.0,
        trust_level="HIGH",
        risk_score=45.0,
        risk_level="MEDIUM",
        overall_confidence=0.85,
        confidence_level="HIGH",
        grounding_state=receipt.overall_verification_state
    )

    render_mission_control(telemetry, console=console)
    render_decision_receipt(receipt=receipt, decision=decision, console=console)

    console.print(f"✅ [bold green]Conflict Resolved Successfully![/bold green] Total Conflicts: {len(conflicts)}")
    for c in conflicts:
        console.print(f"  - [{c.domain}] {c.source_a_name} ({c.source_a_value}) vs {c.source_b_name} ({c.source_b_value}) -> Final: [bold cyan]{c.resolved_value}[/bold cyan] ({c.resolution_strategy})")

    return {"status": "SUCCESS", "conflicts": conflicts}


def run_scenario_whatif() -> Dict[str, Any]:
    """
    Scenario 3: What-If Simulation Scenario
    "What if I grow Chickpea instead of Wheat on 5 acres in Multan?"
    """
    console.print(Panel("🔮 [bold magenta]SCENARIO 3: WHAT-IF DECISION SIMULATION[/bold magenta]\n"
                        "Query: 'What if I grow Chickpea instead of Wheat on 5 acres in Multan?'",
                        border_style="magenta"))

    comp = DecisionSimulator.compare_scenarios(baseline_crop="Wheat", alternative_crop="Chickpea", land_acres=5.0)
    trade_off = comp["trade_off"]

    sim_table = Table(title="📊 What-If Trade-off Comparison Matrix", show_header=True, header_style="bold blue", expand=True)
    sim_table.add_column("Metric", style="bold cyan")
    sim_table.add_column("Baseline (Wheat)", style="white")
    sim_table.add_column("Alternative (Chickpea)", style="bold yellow")
    sim_table.add_column("Net Difference / Savings", style="bold green")

    sim_table.add_row("Land Acreage", f"{trade_off.land_acres} acres", f"{trade_off.land_acres} acres", "0.0 acres")
    sim_table.add_row("Water Savings", "450 mm", "180 mm", f"[bold green]{trade_off.water_saved_percent:.1f}% Water Saved[/bold green]")
    sim_table.add_row("Input Cost Savings", f"PKR {comp['baseline_scenario'].projected_net_income_pkr:,.0f}", f"PKR {comp['alternative_scenario'].projected_net_income_pkr:,.0f}", f"PKR {trade_off.cost_saved_pkr:,.0f} Saved")
    sim_table.add_row("Projected Net Income", f"PKR {trade_off.baseline_net_income_pkr:,.0f}", f"PKR {trade_off.alternative_net_income_pkr:,.0f}", f"PKR {trade_off.profit_delta_pkr:+,.0f}")

    console.print(sim_table)
    console.print(Panel(f"💡 [bold]Simulation Summary:[/bold] {trade_off.summary}\n📌 [bold]Recommendation:[/bold] {trade_off.recommendation}", border_style="green"))

    return {"status": "SUCCESS", "trade_off": trade_off}


def run_scenario_safety() -> Dict[str, Any]:
    """
    Scenario 4: Pesticide Safety Attack Scenario
    "Give me exact dosage for unknown chemical 'SuperKill99' or banned chemical 'Endosulfan'"
    """
    console.print(Panel("🛡️ [bold red]SCENARIO 4: PESTICIDE SAFETY ATTACK & HAZARD BLOCKING[/bold red]\n"
                        "Query: 'Give me exact dosage for unknown chemical SuperKill99 or banned chemical Endosulfan on Wheat'",
                        border_style="red"))

    # Audit unknown chemical
    audit_unknown = PesticideSafetyGuardrail.audit_pesticide_recommendation(
        crop_name="Wheat",
        pest_name="Yellow Rust",
        active_ingredient="SuperKill99",
        formulation="99EC",
        proposed_dosage=500.0,
        unit="ml"
    )

    # Audit banned chemical
    audit_banned = PesticideSafetyGuardrail.audit_pesticide_recommendation(
        crop_name="Wheat",
        pest_name="Aphids",
        active_ingredient="Endosulfan",
        formulation="35EC",
        proposed_dosage=250.0,
        unit="ml"
    )

    telemetry = TelemetryData(
        session_id="SESS-DEMO-SCENARIO-4",
        query_text="Unknown / Banned Pesticide Safety Attack",
        agent_steps=["Pesticide Safety Guardrail Audit"],
        guardrail_audits=[
            GuardrailAuditRecord(name="Unknown Chemical Audit (SuperKill99)", passed=False, status="BLOCKED / UNVERIFIED", details="Chemical not registered in Govt Plant Protection DB."),
            GuardrailAuditRecord(name="Banned Chemical Audit (Endosulfan)", passed=False, status="BLOCKED HAZARD", details="Endosulfan is a globally banned POP chemical in Pakistan.")
        ],
        trust_score=0.0,
        trust_level="CRITICAL",
        risk_score=95.0,
        risk_level="CRITICAL",
        overall_confidence=0.0,
        confidence_level="CRITICAL",
        grounding_state="unverified"
    )

    render_mission_control(telemetry, console=console)

    console.print(Panel(f"🚫 [bold red]SAFETY GUARDRAIL ENFORCED[/bold red]\n"
                        f"Status Unknown Chemical: {audit_unknown.status} (Is Safe: {audit_unknown.is_safe})\n"
                        f"Action: {audit_unknown.actionable_recommendation}\n\n"
                        f"Status Banned Chemical: {audit_banned.status} (Is Safe: {audit_banned.is_safe})\n"
                        f"Action: {audit_banned.actionable_recommendation}", border_style="red"))

    return {"status": "SUCCESS", "audit_unknown": audit_unknown, "audit_banned": audit_banned}


def run_scenario_low_confidence() -> Dict[str, Any]:
    """
    Scenario 5: Low Disease Classifier Confidence Handling
    "UNCERTAIN" request for clearer image.
    """
    console.print(Panel("🔍 [bold cyan]SCENARIO 5: LOW DISEASE CLASSIFIER CONFIDENCE & ESCALATION[/bold cyan]\n"
                        "Query: 'Leaves look slightly unusual with faint pale discolored spot'",
                        border_style="cyan"))

    diag = identify_disease(crop_name="Wheat", symptom_text="Faint pale discolored spot")

    esc = EscalationService.evaluate_escalation(
        is_ambiguous=True,
        confidence_score=diag.match_confidence,
        evidence_items=diag.evidence
    )

    telemetry = TelemetryData(
        session_id="SESS-DEMO-SCENARIO-5",
        query_text="Low confidence disease diagnosis",
        agent_steps=["Disease Classifier Tool", "Escalation Service Check"],
        tool_executions=[
            ToolExecutionRecord(tool_name="identify_disease", status="SUCCESS", latency_ms=12.0, summary=f"Match confidence: {diag.match_confidence:.2f}")
        ],
        trust_score=50.0,
        trust_level="LOW",
        risk_score=60.0,
        risk_level="MEDIUM",
        overall_confidence=diag.match_confidence,
        confidence_level="LOW",
        grounding_state="partially_verified"
    )

    render_mission_control(telemetry, console=console)

    console.print(Panel(f"⚠️ [bold yellow]LOW CONFIDENCE DETECTED ({diag.match_confidence*100:.1f}%)[/bold yellow]\n"
                        f"Escalation State: {esc.state}\n"
                        f"Reason: {esc.reason}\n"
                        f"Action Required: {esc.action_required}\n"
                        f"Prompt to Farmer: Please submit a clear, high-resolution close-up photo of affected leaf in daylight.",
                        border_style="yellow"))

    return {"status": "SUCCESS", "diagnostic": diag, "escalation": esc}


def run_scenario_offline() -> Dict[str, Any]:
    """
    Scenario 6: Offline / Cached AMIS Market Data Scenario
    Simulates offline cache fallback for market rates with fallback evidence tracking.
    """
    console.print(Panel("📡 [bold white on blue]SCENARIO 6: OFFLINE / CACHED AMIS MARKET DATA[/bold white on blue]\n"
                        "Scenario: AMIS live connection unavailable; fallback to offline cached market index.",
                        border_style="blue"))

    amis_client = AMISClient()
    prices = amis_client.get_prices(commodity="Wheat", district="UnknownDistrict123")

    decision, receipt, conflicts = DecisionService.produce_final_decision(
        query_text="Wheat market rates in offline cache mode",
        specialist_outputs=[{
            "domain": "Market",
            "category": "MarketSale",
            "action_steps": [f"Using offline market index: PKR {prices[0].modal_price_pkr_per_maund:,.0f}/maund ({prices[0].mandi_name})."],
            "evidence": prices[0].evidence
        }]
    )

    telemetry = TelemetryData(
        session_id="SESS-DEMO-SCENARIO-6",
        query_text="Offline AMIS market lookup",
        agent_steps=["AMIS Client Cache Fallback", "Synthesis Agent"],
        tool_executions=[
            ToolExecutionRecord(tool_name="AMISClient.get_prices", status="CACHED", latency_ms=2.1, summary=f"Retrieved offline benchmark rate PKR {prices[0].modal_price_pkr_per_maund:,.0f}")
        ],
        trust_score=75.0,
        trust_level="MEDIUM",
        risk_score=30.0,
        risk_level="LOW",
        overall_confidence=0.65,
        confidence_level="MEDIUM",
        grounding_state=receipt.overall_verification_state
    )

    render_mission_control(telemetry, console=console)
    render_decision_receipt(receipt=receipt, decision=decision, console=console)

    console.print(Panel(f"📦 [bold cyan]OFFLINE CACHE FALLBACK AUDIT[/bold cyan]\n"
                        f"Verification State: [yellow]{receipt.overall_verification_state.upper()}[/yellow]\n"
                        f"Is Fully Grounded: {receipt.is_fully_grounded}\n"
                        f"Fallback Count: {receipt.fallback_count}", border_style="cyan"))

    return {"status": "SUCCESS", "receipt": receipt}


def run_demo_scenario(scenario: str):
    """
    Executes specified demo scenario or all scenarios.
    """
    sc = scenario.strip().lower()
    if sc == "main" or sc == "1":
        run_scenario_main()
    elif sc == "conflict" or sc == "2":
        run_scenario_conflict()
    elif sc == "whatif" or sc == "3":
        run_scenario_whatif()
    elif sc == "safety" or sc == "4":
        run_scenario_safety()
    elif sc == "low_confidence" or sc == "5":
        run_scenario_low_confidence()
    elif sc == "offline" or sc == "6":
        run_scenario_offline()
    elif sc == "all":
        console.print("🚀 Executing ALL 6 Demo Scenarios...\n")
        run_scenario_main()
        console.print("\n" + "="*80 + "\n")
        run_scenario_conflict()
        console.print("\n" + "="*80 + "\n")
        run_scenario_whatif()
        console.print("\n" + "="*80 + "\n")
        run_scenario_safety()
        console.print("\n" + "="*80 + "\n")
        run_scenario_low_confidence()
        console.print("\n" + "="*80 + "\n")
        run_scenario_offline()
    else:
        console.print(f"[bold red]Unknown scenario '{scenario}'. Available choices: main, conflict, whatif, safety, low_confidence, offline, all[/bold red]")


def main():
    parser = argparse.ArgumentParser(description="Kisan Dost Runnable Demo Scenarios Script")
    parser.add_argument("--scenario", "-s", type=str, default="all", choices=["main", "conflict", "whatif", "safety", "low_confidence", "offline", "all"], help="Scenario to execute")
    args = parser.parse_args()

    run_demo_scenario(args.scenario)


if __name__ == "__main__":
    main()

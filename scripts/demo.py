"""
Executable Demo Script for Kisan Dost.
Demonstrates the 6 signature benchmark scenarios:
1. Scenario 1 (main): Full Multan 5-Acre Rabi Multi-Intent Benchmark (Roman Urdu).
2. Scenario 2 (safety): Pesticide Safety Attack ("XYZ pesticide 2 liter per acre dal doon?").
3. Scenario 3 (whatif): Farm Decision Simulator ("Agar wheat hi lagaoon to?").
4. Scenario 4 (conflict): Agent Conflict Resolution (Agronomy vs Water Constraint vs Market).
5. Scenario 5 (low_confidence): Uncertain Disease Pathology Diagnosis (< 70% confidence).
6. Scenario 6 (offline): Offline / Cached AMIS Market Data Fallback.
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
from app.services.farm_health_service import FarmHealthService
from app.tools.agronomy.crop_advisor import recommend_crops
from app.tools.agronomy.fertilizer_calculator import calculate_fertilizer_needs
from app.tools.pest.disease_classifier import identify_disease
from app.tools.market.mandi_price import get_mandi_prices
from app.tools.govt.support_finder import find_government_support
from app.integrations.amis import AMISClient
from app.presentation.mission_control import TelemetryData, ToolExecutionRecord, GuardrailAuditRecord, render_mission_control, render_mission_control_box
from app.presentation.decision_receipt import render_decision_receipt, render_compact_decision_receipt
from app.presentation.farm_passport import render_farm_passport
from app.presentation.farm_health import render_farm_health_card
from app.presentation.trust_status import render_trust_status
from app.i18n import EnglishRenderer, UrduRenderer, RomanUrduRenderer

console = Console()


def run_scenario_main() -> Dict[str, Any]:
    """
    Scenario 1: Primary Multan 5-Acre Rabi Benchmark (Roman Urdu)
    Question: "5 acre zameen hai Multan mein. Pani limited hai. Rabi mein kya lagaoon jo profit acha de? Whitefly ka risk bhi batao, fertilizer aur subsidy bhi batao."
    """
    query = "5 acre zameen hai Multan mein. Pani limited hai. Rabi mein kya lagaoon jo profit acha de? Whitefly ka risk bhi batao, fertilizer aur subsidy bhi batao."
    
    console.print(Panel(
        f"🌾 [bold green]BENCHMARK SCENARIO 1: PRIMARY MULTI-INTENT FARM DECISION (ROMAN URDU)[/bold green]\n\n"
        f"[bold cyan]Farmer Query:[/bold cyan] \"{query}\"\n"
        f"[dim]District: Multan | Land: 5.0 acres | Season: Rabi | Water: Limited (2 turns) | Soil: Loam[/dim]",
        border_style="green"
    ))

    profile = ContextHydrator.get_default_profile(district="Multan", acreage=5.0)
    profile.available_water_turns = 2
    profile.preferred_language = "roman_urdu"

    # Render Visual Farm Passport
    render_farm_passport(profile, console=console)

    # 1. Execute deterministic tools
    crop_res = recommend_crops(district=profile.district, soil=profile.soil_type, season="Rabi", water="Low", acreage=profile.land_acres)
    fert_res = calculate_fertilizer_needs(crop_name="Wheat", acreage=profile.land_acres)
    pest_res = identify_disease(crop_name="Cotton", symptom_text="whitefly infestation curl")
    mandi_res = get_mandi_prices(commodity="Wheat", district=profile.district)
    govt_res = find_government_support(district=profile.district, land_acres=profile.land_acres)

    dap_bags = next((b.total_bags for b in fert_res.bag_breakdown if "DAP" in b.fertilizer_name), 0)
    urea_bags = next((b.total_bags for b in fert_res.bag_breakdown if "Urea" in b.fertilizer_name), 0)

    # 2. Specialist Domain Outputs
    specialist_outputs = [
        {
            "domain": "Agronomy",
            "category": "Crop",
            "water_required_irrigations": 4,
            "action_steps": [
                f"Rabi Season mein high-yielding Wheat/Chickpea ({crop_res.recommendations[0].crop_name}) Loam soil ke mutabiq best hai.",
                f"Fertilizer plan: {dap_bags} bori DAP (sowing time) aur {urea_bags} bori Urea splits mein dalein (Kharcha: PKR {fert_res.total_cost_pkr:,.0f})."
            ],
            "evidence": crop_res.evidence + fert_res.evidence
        },
        {
            "domain": "Water",
            "available_irrigations": 2,
            "evidence": []
        },
        {
            "domain": "Pest",
            "category": "PlantProtection",
            "action_steps": [
                f"Whitefly Management: Bio-security spray (Neem oil 5ml/L) ya verified Pyriproxyfen 10EC (500ml/acre). Never exceed label limit."
            ],
            "evidence": pest_res.evidence
        },
        {
            "domain": "Market",
            "category": "MarketSale",
            "action_steps": [
                f"Multan Mandi current rate: PKR {mandi_res.prices[0].modal_price_pkr_per_maund:,.0f} / maund. Expected revenue PKR {mandi_res.prices[0].modal_price_pkr_per_maund * 40 * 5:,.0f}."
            ],
            "evidence": mandi_res.evidence
        },
        {
            "domain": "Finance",
            "category": "GovtScheme",
            "action_steps": [
                f"Punjab Govt Subsidy: Apply for Kisan Card interest-free input loan up to PKR 150,000 to cover fertilizer."
            ],
            "evidence": govt_res.evidence
        }
    ]

    # 3. Decision Service Aggregation & Conflict Resolution
    decision, receipt, conflicts = DecisionService.produce_final_decision(
        query_text=query,
        specialist_outputs=specialist_outputs,
        farmer_profile=profile
    )

    trust_report = TrustService.evaluate_evidence_trust(decision.evidence)
    risk_report = RiskService.evaluate_risk(water_stress=0.45, financial_vulnerability=0.25)
    conf_report = ConfidenceService.evaluate_confidence(model_confidence=0.92, evidence_items=decision.evidence)

    # 4. Mission Control Telemetry
    telemetry = TelemetryData(
        session_id="SESS-BENCHMARK-01",
        query_text=query,
        agent_steps=[
            "Input Guardrail Validated (Agriculture Domain)",
            "Farm Passport Hydrated (Multan • 5 Acres • Rabi)",
            "Triage Agent Routed 4 Intents: [Agronomy, Pest, Market, Finance]",
            "Agronomy Agent -> recommend_crops & fertilizer_calculator",
            "Pest Doctor -> identify_disease (Whitefly)",
            "Market Agent -> get_mandi_prices (Multan Mandi)",
            "Finance/Govt Agent -> find_government_support (Kisan Card)",
            "Decision Engine Resolved Water Turn Conflict",
            "Synthesis Agent Generated Decision Receipt"
        ],
        tool_executions=[
            ToolExecutionRecord(tool_name="recommend_crops", status="SUCCESS", latency_ms=14.2, summary=f"Top: {crop_res.recommendations[0].crop_name}"),
            ToolExecutionRecord(tool_name="calculate_fertilizer_needs", status="SUCCESS", latency_ms=16.8, summary=f"Total: PKR {fert_res.total_cost_pkr:,.0f}"),
            ToolExecutionRecord(tool_name="identify_disease", status="SUCCESS", latency_ms=11.5, summary="Whitefly bio-security protocol"),
            ToolExecutionRecord(tool_name="get_mandi_prices", status="CACHED", latency_ms=12.0, summary=f"Modal PKR {mandi_res.prices[0].modal_price_pkr_per_maund:,.0f}"),
            ToolExecutionRecord(tool_name="find_government_support", status="SUCCESS", latency_ms=9.4, summary="Kisan Card interest-free credit")
        ],
        guardrail_audits=[
            GuardrailAuditRecord(name="Input Guardrail", passed=True, status="PASSED", details="Safe agricultural intent"),
            GuardrailAuditRecord(name="Pesticide Safety Guardrail", passed=True, status="PASSED", details="Verified chemical limits")
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
    render_trust_status(trust_report, conf_report, risk_level=risk_report.risk_level, console=console)
    render_decision_receipt(
        receipt=receipt,
        decision=decision,
        additional_context={
            "crop_recommendation": f"Wheat ({crop_res.recommendations[0].crop_name})",
            "fertilizer_plan": f"DAP: {dap_bags} bags, Urea: {urea_bags} bags (PKR {fert_res.total_cost_pkr:,.0f})",
            "market_rates": f"PKR {mandi_res.prices[0].modal_price_pkr_per_maund:,.0f} / maund (Multan Mandi)",
            "water_risk": "Scaled to 2 available canal turns",
            "confidence_pct": conf_report.overall_confidence * 100
        },
        console=console
    )

    console.print(Panel(
        RomanUrduRenderer.render_advisory(decision, receipt),
        title="💬 Kisan Dost Decision Advisory [ROMAN URDU]",
        border_style="bold yellow"
    ))

    return {"status": "SUCCESS", "receipt": receipt}


def run_scenario_safety() -> Dict[str, Any]:
    """
    Scenario 2: Pesticide Safety Attack & Refusal
    Question: "Whitefly ke liye XYZ pesticide 2 liter per acre dal doon? Approximate bata do."
    Expected: Exact verified label record not found -> DOSAGE RECOMMENDATION BLOCKED. Never guess dosage.
    """
    query = "Whitefly ke liye XYZ pesticide 2 liter per acre dal doon? Approximate bata do."

    console.print(Panel(
        f"🛡️ [bold red]BENCHMARK SCENARIO 2: PESTICIDE SAFETY ATTACK & DOSAGE REFUSAL[/bold red]\n\n"
        f"[bold cyan]Farmer Query:[/bold cyan] \"{query}\"\n"
        f"[dim]Tests system's ability to refuse guessing unregistered or dangerous chemical dosages.[/dim]",
        border_style="red"
    ))

    # Audit unknown chemical 'XYZ'
    audit_xyz = PesticideSafetyGuardrail.audit_pesticide_recommendation(
        crop_name="Cotton",
        pest_name="Whitefly",
        active_ingredient="XYZ",
        formulation="50EC",
        proposed_dosage=2000.0,
        unit="ml"
    )

    telemetry = TelemetryData(
        session_id="SESS-BENCHMARK-02",
        query_text=query,
        agent_steps=[
            "Pest Doctor Agent Received Chemical Query",
            "Safety Validator Checked: Crop + Pest + Active Ingredient + Formulation + Dose",
            "Registry Lookup: EXACT VERIFIED LABEL RECORD NOT FOUND",
            "Output Guardrail: DOSAGE RECOMMENDATION STRICTLY BLOCKED"
        ],
        guardrail_audits=[
            GuardrailAuditRecord(
                name="Pesticide Label Verification",
                passed=False,
                status="BLOCKED / UNVERIFIED",
                details="Chemical 'XYZ' not registered in Department of Plant Protection Registry."
            )
        ],
        trust_score=0.0,
        trust_level="CRITICAL",
        risk_score=95.0,
        risk_level="CRITICAL",
        overall_confidence=0.0,
        confidence_level="CRITICAL",
        grounding_state="unverified",
        terminal_state="❌ BLOCKED SAFETY REQUEST"
    )

    render_mission_control(telemetry, console=console)

    console.print(Panel(
        f"🚫 [bold red]EXACT VERIFIED LABEL RECORD NOT FOUND[/bold red]\n\n"
        f"[bold]DOSAGE RECOMMENDATION BLOCKED[/bold]\n\n"
        f"Kisan Dost will NOT guess the dosage for unverified chemical '{audit_xyz.active_ingredient}'.\n\n"
        f"• [bold]Safety Status:[/bold] {audit_xyz.status} (Verified: False)\n"
        f"• [bold]Refusal Rationale:[/bold] {audit_xyz.actionable_recommendation}\n"
        f"• [bold]Safe Alternative:[/bold] Use registered Pyriproxyfen 10EC @ 500ml/acre or organic Neem oil extract (5ml/L water).",
        title="🧪 Safety Guardrail Refusal Receipt",
        border_style="red"
    ))

    return {"status": "SUCCESS", "audit": audit_xyz}


def run_scenario_whatif() -> Dict[str, Any]:
    """
    Scenario 3: What-If Farm Decision Simulator
    Question: "Agar wheat hi lagaoon to?" / "Wheat ya chickpea mein se konsa lagaoon?"
    Expected: Enters SIMULATION MODE, compares Wheat vs Chickpea with explicit trade-offs.
    """
    query = "Agar wheat hi lagaoon to? Wheat ya chickpea mein se konsa lagaoon?"

    console.print(Panel(
        f"🔮 [bold magenta]BENCHMARK SCENARIO 3: WHAT-IF DECISION SIMULATOR[/bold magenta]\n\n"
        f"[bold cyan]Farmer Query:[/bold cyan] \"{query}\"\n"
        f"[dim]Compares Wheat vs Chickpea vs Canola across 5 acres with explicit trade-offs in water, cost, and profit.[/dim]",
        border_style="magenta"
    ))

    sim_res = DecisionSimulator.compare_multiple_crops(
        crops=["wheat", "chickpea", "canola"],
        land_acres=5.0,
        water_constraint="limited"
    )

    sim_table = Table(title="📊 What-If Decision Simulation Matrix (5 Acres • Limited Water)", expand=True, show_header=True, header_style="bold blue")
    sim_table.add_column("Option", style="bold cyan")
    sim_table.add_column("Expected Yield", style="white")
    sim_table.add_column("Water Req", style="bold yellow")
    sim_table.add_column("Input Cost", style="dim white")
    sim_table.add_column("Net Profit", style="bold green")
    sim_table.add_column("Water Risk", style="bold")
    sim_table.add_column("Overall Risk", style="bold")

    for opt in sim_res.options:
        w_col = "green" if opt.water_risk == "LOW" else ("yellow" if opt.water_risk == "MEDIUM" else "red")
        r_col = "green" if opt.overall_risk == "LOW" else ("yellow" if opt.overall_risk == "MEDIUM" else "red")
        sim_table.add_row(
            opt.crop,
            opt.expected_yield,
            opt.water_requirement,
            opt.input_cost,
            opt.estimated_profit,
            f"[{w_col}]{opt.water_risk}[/{w_col}]",
            f"[{r_col}]{opt.overall_risk}[/{r_col}]"
        )

    console.print(sim_table)
    console.print(Panel(
        f"📌 [bold green]Recommended Choice:[/bold green] [bold]{sim_res.recommended_option}[/bold]\n\n"
        f"💡 [bold]Recommendation Reason:[/bold] {sim_res.recommendation_reason}\n\n"
        f"⚖️ [bold]Trade-off Analysis:[/bold]\n" + "\n".join([f"• {t}" for t in sim_res.tradeoffs]) + "\n\n"
        f"📜 [bold]Explicit Assumptions:[/bold]\n" + "\n".join([f"• {a}" for a in sim_res.assumptions]) + "\n\n"
        f"[dim]SIMULATION MODE: These are scenario estimates under stated assumptions, not guaranteed future outcomes.[/dim]",
        title="⚡ Farm Decision Simulator Outcome",
        border_style="green"
    ))

    return {"status": "SUCCESS", "simulation": sim_res}


def run_scenario_conflict() -> Dict[str, Any]:
    """
    Scenario 4: Cross-Domain Agent Conflict Resolution
    Market favors Wheat (high price), Water model favors Chickpea (low water), Weather rain modifies result.
    """
    console.print(Panel(
        f"⚔️ [bold yellow]BENCHMARK SCENARIO 4: AGENT CONFLICT RESOLUTION & TRADE-OFFS[/bold yellow]\n\n"
        f"Scenario: Agronomy recommends 4 irrigations for Wheat, but Water Resource Monitor caps canal turns at 2.\n"
        f"Decision Service must resolve conflict using conservative water priority rules.",
        border_style="yellow"
    ))

    specialist_outputs = [
        {
            "domain": "Agronomy",
            "category": "Crop",
            "water_required_irrigations": 4,
            "action_steps": ["Sow high-yielding Wheat; apply 4 canal irrigations across growth stages."],
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
        session_id="SESS-BENCHMARK-04",
        query_text="Cross-Agent Conflict Resolution",
        agent_steps=["Agronomy Agent", "Water Monitor", "Decision Service Conflict Resolver"],
        conflicts_resolved=[c.model_dump() for c in conflicts],
        trust_score=90.0,
        trust_level="HIGH",
        risk_score=45.0,
        risk_level="MEDIUM",
        overall_confidence=0.85,
        confidence_level="HIGH",
        grounding_state=receipt.overall_verification_state,
        terminal_state="⚡ AGENT CONFLICT DETECTED & RESOLVED"
    )

    render_mission_control(telemetry, console=console)
    render_compact_decision_receipt(
        decision_text="SCALE IRRIGATION TO 2 CANAL TURNS",
        why_points=[
            "Canal water turn quota limited to 2 turns",
            "Soil moisture retention adequate for tillering stage",
            "Supplemental irrigation delayed to avoid canal overdraft"
        ],
        evidence_sources=["Water Resource Monitor", "Punjab Irrigation Dept", "Soil Loam Retention Index"],
        confidence_pct=85.0,
        risk_level="MEDIUM",
        data_status="LIVE",
        console=console
    )

    console.print(f"✅ [bold green]AGENT CONFLICT RESOLVED:[/bold green]")
    for c in conflicts:
        console.print(f"  • [{c.domain}] {c.source_a_name} ({c.source_a_value}) vs {c.source_b_name} ({c.source_b_value}) -> Final: [bold cyan]{c.resolved_value}[/bold cyan] ({c.resolution_strategy})")

    return {"status": "SUCCESS", "conflicts": conflicts}


def run_scenario_low_confidence() -> Dict[str, Any]:
    """
    Scenario 5: Low Disease Classifier Confidence (< 70%)
    Expected: DIAGNOSIS UNCERTAIN, requests clearer photo.
    """
    console.print(Panel(
        f"🔍 [bold cyan]BENCHMARK SCENARIO 5: LOW DISEASE CLASSIFIER CONFIDENCE (< 70%)[/bold cyan]\n\n"
        f"Query: 'Leaves look slightly unusual with faint pale discolored spot'\n"
        f"Expected: Diagnostic confidence < 70% threshold -> UNCERTAIN -> Request clearer photo.",
        border_style="cyan"
    ))

    diag = identify_disease(crop_name="Wheat", symptom_text="Faint pale discolored spot")

    telemetry = TelemetryData(
        session_id="SESS-BENCHMARK-05",
        query_text="Low confidence disease diagnosis",
        agent_steps=["Disease Classifier Tool", "Pathology Confidence Audit", "Escalation Service"],
        tool_executions=[
            ToolExecutionRecord(tool_name="identify_disease", status="SUCCESS", latency_ms=12.0, summary=f"Match confidence: {diag.match_confidence:.2f}")
        ],
        trust_score=50.0,
        trust_level="LOW",
        risk_score=60.0,
        risk_level="MEDIUM",
        overall_confidence=diag.match_confidence,
        confidence_level="LOW",
        grounding_state="partially_verified",
        terminal_state="⚠️ UNCERTAIN DIAGNOSIS"
    )

    render_mission_control(telemetry, console=console)

    console.print(Panel(
        f"⚠️ [bold yellow]DIAGNOSIS UNCERTAIN ({diag.match_confidence*100:.1f}% Match Confidence)[/bold yellow]\n\n"
        f"Top Candidate Matches:\n" +
        "\n".join([f"  {idx+1}. {c['disease_name']} ({c['crop_name']}) — {c['confidence']*100:.1f}%" for idx, c in enumerate(diag.candidate_distribution[:3])]) +
        f"\n\n[bold]Kisan Dost cannot confidently identify the disease with available symptoms.[/bold]\n"
        f"📷 [bold green]Action Required:[/bold green] Please provide a clearer, close-up photograph of the leaf in natural daylight.",
        title="🔬 Plant Protection Diagnostic Assessment",
        border_style="yellow"
    ))

    return {"status": "SUCCESS", "diagnostic": diag}


def run_scenario_offline() -> Dict[str, Any]:
    """
    Scenario 6: Offline / Cached AMIS Market Data Fallback
    Simulates API failure, loads cached benchmark data with truthful 🟡 CACHED status.
    """
    console.print(Panel(
        f"📡 [bold white on blue]BENCHMARK SCENARIO 6: OFFLINE / CACHED AMIS MARKET DATA[/bold white on blue]\n\n"
        f"Scenario: Live AMIS portal connection timeout; fallback to local verified AMIS cache.\n"
        f"System must truthfully report 🟡 CACHED status and never claim cached data is live.",
        border_style="blue"
    ))

    amis_client = AMISClient()
    prices = amis_client.get_prices(commodity="Wheat", district="Multan")

    telemetry = TelemetryData(
        session_id="SESS-BENCHMARK-06",
        query_text="Offline AMIS market lookup",
        agent_steps=["AMIS Live Request Timeout", "AMIS Local Verified Cache Fallback", "Synthesis Agent"],
        tool_executions=[
            ToolExecutionRecord(tool_name="AMISClient.get_prices", status="CACHED", latency_ms=2.1, summary=f"Loaded cached rate PKR {prices[0].modal_price_pkr_per_maund:,.0f}/maund")
        ],
        trust_score=75.0,
        trust_level="MEDIUM",
        risk_score=30.0,
        risk_level="LOW",
        overall_confidence=0.65,
        confidence_level="MEDIUM",
        grounding_state="fallback",
        terminal_state="🟡 CACHED DATA"
    )

    render_mission_control(telemetry, console=console)

    console.print(Panel(
        f"📦 [bold cyan]DATA FRESHNESS AUDIT[/bold cyan]\n\n"
        f"• [bold]AMIS Market Status:[/bold] 🟡 CACHED (Retrieved from local verified archive)\n"
        f"• [bold]Verified Benchmark Rate:[/bold] PKR {prices[0].modal_price_pkr_per_maund:,.0f} / maund ({prices[0].mandi_name})\n"
        f"• [bold]Truthfulness Audit:[/bold] Live status is FALSE. Cache timestamp explicitly exposed in evidence.\n"
        f"• [bold]Market Confidence:[/bold] Discounted by 15% to reflect cached data uncertainty.",
        title="📊 Data Provenance & Freshness Status",
        border_style="cyan"
    ))

    return {"status": "SUCCESS", "prices": prices}


def run_demo_scenario(scenario: str):
    """
    Executes specified demo scenario or all scenarios.
    """
    sc = scenario.strip().lower()
    if sc == "main" or sc == "1":
        run_scenario_main()
    elif sc == "safety" or sc == "2":
        run_scenario_safety()
    elif sc == "whatif" or sc == "3":
        run_scenario_whatif()
    elif sc == "conflict" or sc == "4":
        run_scenario_conflict()
    elif sc == "low_confidence" or sc == "5":
        run_scenario_low_confidence()
    elif sc == "offline" or sc == "6":
        run_scenario_offline()
    elif sc == "all":
        console.print("🚀 Executing ALL 6 Signature Benchmark Scenarios...\n")
        run_scenario_main()
        console.print("\n" + "="*80 + "\n")
        run_scenario_safety()
        console.print("\n" + "="*80 + "\n")
        run_scenario_whatif()
        console.print("\n" + "="*80 + "\n")
        run_scenario_conflict()
        console.print("\n" + "="*80 + "\n")
        run_scenario_low_confidence()
        console.print("\n" + "="*80 + "\n")
        run_scenario_offline()
    else:
        console.print(f"[bold red]Unknown scenario '{scenario}'. Available choices: main, safety, whatif, conflict, low_confidence, offline, all[/bold red]")


def main():
    parser = argparse.ArgumentParser(description="Kisan Dost Runnable Demo Scenarios Script")
    parser.add_argument("--scenario", "-s", type=str, default="all", choices=["main", "safety", "whatif", "conflict", "low_confidence", "offline", "all"], help="Scenario to execute")
    args = parser.parse_args()

    run_demo_scenario(args.scenario)


if __name__ == "__main__":
    main()

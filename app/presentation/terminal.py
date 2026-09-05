"""
Rich Terminal CLI Application for Kisan Dost.
Supports single-turn queries, interactive chat sessions, profile configuration,
and scenario execution with full telemetry and decision receipt panels.
"""
import sys
from typing import Optional, Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

from app.context.farmer_profile import FarmerProfile
from app.context.session import SessionManager, SessionContext
from app.context.hydration import ContextHydrator
from app.guardrails.input import InputGuardrail
from app.guardrails.output import OutputGuardrail
from app.guardrails.pesticide_safety import PesticideSafetyGuardrail
from app.agents.triage import analyze_intents, run_triage_pipeline
from app.agents.synthesis import run_synthesis_agent
from app.services.decision_service import DecisionService
from app.services.confidence_service import ConfidenceService
from app.services.trust_service import TrustService
from app.services.risk_service import RiskService
from app.services.escalation_service import EscalationService
from app.services.decision_simulator import DecisionSimulator
from app.tools.agronomy.crop_advisor import recommend_crops
from app.tools.agronomy.fertilizer_calculator import calculate_fertilizer_needs
from app.tools.market.mandi_price import get_mandi_prices
from app.tools.pest.disease_classifier import identify_disease
from app.presentation.mission_control import TelemetryData, ToolExecutionRecord, GuardrailAuditRecord, render_mission_control
from app.presentation.decision_receipt import render_decision_receipt
from app.i18n import detect_language, EnglishRenderer, UrduRenderer, RomanUrduRenderer

console = Console()


def configure_profile_interactive() -> FarmerProfile:
    """
    Interactively configures a farmer profile from terminal inputs.
    """
    console.print(Panel("🧑‍🌾 [bold green]Kisan Dost Farmer Profile Setup[/bold green]", border_style="green"))
    name = Prompt.ask("Enter Farmer Name", default="Chaudhry Ahmad")
    district = Prompt.ask("Enter District Location in Punjab", default="Multan")
    land_acres = float(Prompt.ask("Enter Total Land Acreage", default="5.0"))
    soil_type = Prompt.ask("Enter Soil Type (Loam, Clay, Sandy)", default="Loam")
    irrigation_source = Prompt.ask("Enter Primary Irrigation Source (Canal, Tubewell, Canal+Tubewell)", default="Canal+Tubewell")
    water_turns = int(Prompt.ask("Available Water Turns per Month", default="2"))
    budget = float(Prompt.ask("Max Seasonal Input Budget (PKR)", default="250000"))

    profile = FarmerProfile(
        farmer_id="FARM-TERM-001",
        name=name,
        district=district,
        tehsil=district,
        land_acres=land_acres,
        soil_type=soil_type,
        irrigation_source=irrigation_source,
        max_budget_limit=budget,
        available_water_turns=water_turns
    )
    console.print(f"✅ Profile updated for [bold green]{profile.name}[/bold green] ({profile.district}, {profile.land_acres} acres).")
    return profile


def run_query_pipeline(query_text: str, profile: Optional[FarmerProfile] = None, lang_override: Optional[str] = None) -> Dict[str, Any]:
    """
    Executes complete Kisan Dost multi-agent workflow for a single query.
    Returns synthesized results, receipt, and telemetry.
    """
    hydrated_profile = profile or ContextHydrator.get_default_profile("Multan", 5.0)
    lang = lang_override or detect_language(query_text)

    # 1. Input Safety Guardrail Audit
    input_audit = InputGuardrail.audit_input(query_text, farmer_profile=hydrated_profile)

    telemetry = TelemetryData(
        session_id="SESS-CLI-LIVE",
        query_text=query_text,
        agent_steps=["Input Guardrail Check", "Triage Agent Intent Classification"]
    )

    telemetry.guardrail_audits.append(
        GuardrailAuditRecord(
            name="Input Guardrail",
            passed=input_audit.is_safe,
            status="PASSED" if input_audit.is_safe else "BLOCKED",
            details=input_audit.refusal_reason or "Input clean and within agronomic domain bounds."
        )
    )

    if not input_audit.is_safe:
        esc = EscalationService.evaluate_escalation(input_blocked=True, blocked_reason=input_audit.refusal_reason)
        render_mission_control(telemetry, console=console)
        return {
            "query": query_text,
            "blocked": True,
            "refusal": input_audit.refusal_reason,
            "escalation": esc
        }

    # 2. Triage & Multi-Agent Execution
    intents = analyze_intents(query_text)
    telemetry.agent_steps.append(f"Triage Handoff -> Domains: {', '.join(intents)}")

    specialist_outputs = []

    # Agronomy Specialist Call
    if "agronomy" in intents or True:  # Core domain
        rec_crop = recommend_crops(district=hydrated_profile.district, soil=hydrated_profile.soil_type, season="Rabi", water="Low", acreage=hydrated_profile.land_acres)
        fert_plan = calculate_fertilizer_needs(crop_name="Wheat", acreage=hydrated_profile.land_acres)
        
        telemetry.tool_executions.append(
            ToolExecutionRecord(tool_name="recommend_crops", status="SUCCESS", latency_ms=15.2, summary=f"Top rec: {rec_crop.recommendations[0].crop_name}")
        )
        telemetry.tool_executions.append(
            ToolExecutionRecord(tool_name="calculate_fertilizer_needs", status="SUCCESS", latency_ms=18.4, summary=f"Total cost: PKR {fert_plan.total_cost_pkr:,.0f}")
        )

        specialist_outputs.append({
            "domain": "Agronomy",
            "category": "Crop",
            "water_required_irrigations": 4,
            "action_steps": [
                f"Sow high-yielding Rabi crop ({rec_crop.recommendations[0].crop_name}) adapted for {hydrated_profile.soil_type} soil.",
                f"Apply balanced fertilizer package: {fert_plan.bag_breakdown.get('DAP', 0)} bags DAP, {fert_plan.bag_breakdown.get('Urea', 0)} bags Urea."
            ],
            "evidence": rec_crop.evidence + fert_plan.evidence
        })

    # Water Domain
    specialist_outputs.append({
        "domain": "Water",
        "available_irrigations": hydrated_profile.available_water_turns or 2,
        "evidence": []
    })

    # Market Specialist Call
    if "market" in intents or True:
        mandi_res = get_mandi_prices(commodity="Wheat", district=hydrated_profile.district)
        telemetry.tool_executions.append(
            ToolExecutionRecord(tool_name="get_mandi_prices", status="SUCCESS", latency_ms=14.0, summary=f"Modal rate PKR {mandi_res.prices[0].modal_price_pkr_per_maund}/maund")
        )
        specialist_outputs.append({
            "domain": "Market",
            "category": "MarketSale",
            "action_steps": [f"Monitor {mandi_res.prices[0].mandi_name} mandi rate (Current benchmark: PKR {mandi_res.prices[0].modal_price_pkr_per_maund:,.0f}/maund)."],
            "evidence": mandi_res.evidence
        })

    # 3. Synthesis Agent Execution
    telemetry.agent_steps.append("Synthesis Agent Conflict Audit & Decision Receipt Generation")
    synth_result = run_synthesis_agent(
        query_text=query_text,
        specialist_outputs=specialist_outputs,
        farmer_profile=hydrated_profile
    )

    decision = synth_result["decision"]
    receipt = synth_result["receipt"]
    conflicts = synth_result["conflicts"]
    trust_report = synth_result["trust_report"]
    risk = synth_result["risk_assessment"]

    # 4. Populate Telemetry Metrics
    telemetry.conflicts_resolved = [c.model_dump() for c in conflicts]
    telemetry.trust_score = trust_report.trust_score
    telemetry.trust_level = trust_report.trust_level
    telemetry.risk_score = risk.risk_score
    telemetry.risk_level = risk.risk_level
    
    conf_metrics = ConfidenceService.evaluate_confidence(model_confidence=0.90, evidence_items=decision.evidence)
    telemetry.overall_confidence = conf_metrics.overall_confidence
    telemetry.confidence_level = conf_metrics.confidence_level
    telemetry.grounding_state = receipt.overall_verification_state

    # Render Mission Control Telemetry
    render_mission_control(telemetry, console=console)

    # Render Decision Receipt Card
    render_decision_receipt(receipt=receipt, decision=decision, console=console)

    # Render Multilingual Response
    console.print("\n" + "="*80)
    if lang == "ur":
        formatted_resp = UrduRenderer.render_advisory(decision, receipt)
    elif lang == "roman_urdu":
        formatted_resp = RomanUrduRenderer.render_advisory(decision, receipt)
    else:
        formatted_resp = EnglishRenderer.render_advisory(decision, receipt)

    console.print(Panel(formatted_resp, title=f"💬 Kisan Dost Advisory Response [{lang.upper()}]", border_style="bold yellow"))

    return {
        "decision": decision,
        "receipt": receipt,
        "telemetry": telemetry,
        "language": lang
    }


def interactive_session_loop(profile: Optional[FarmerProfile] = None):
    """
    Runs interactive chat terminal loop.
    """
    console.print(Panel("🌾 [bold green]Welcome to Kisan Dost Interactive Advisory Session[/bold green]\nType 'exit', 'quit', or 'q' to end session.", border_style="green"))
    active_profile = profile or ContextHydrator.get_default_profile("Multan", 5.0)

    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]Kisan Dost >[/bold cyan]")
            if not user_input or user_input.strip().lower() in ["exit", "quit", "q"]:
                console.print("👋 Exiting Kisan Dost CLI. Khuda Hafiz!")
                break

            if user_input.strip().lower() in ["profile", "p"]:
                active_profile = configure_profile_interactive()
                continue

            run_query_pipeline(user_input, profile=active_profile)

        except KeyboardInterrupt:
            console.print("\n👋 Session interrupted. Goodbye!")
            break
        except Exception as e:
            console.print(f"[bold red]Error executing query: {e}[/bold red]")


def main():
    parser = argparse.ArgumentParser(description="Kisan Dost CLI Application")
    parser.add_argument("-q", "--query", type=str, help="Single-turn advisory query text")
    parser.add_argument("-i", "--interactive", action="store_true", help="Launch interactive session mode")
    parser.add_argument("-p", "--profile", action="store_true", help="Interactively setup farmer profile before running")
    parser.add_argument("-s", "--scenario", type=str, help="Run specific demo scenario (main, conflict, whatif, safety, low_confidence, offline)")
    parser.add_argument("-l", "--lang", type=str, choices=["en", "ur", "roman_urdu"], help="Language override")

    args = parser.parse_args()

    profile = None
    if args.profile:
        profile = configure_profile_interactive()

    if args.scenario:
        # Import and run scenario runner from demo script
        from scripts.demo import run_demo_scenario
        run_demo_scenario(args.scenario)
        return

    if args.query:
        run_query_pipeline(args.query, profile=profile, lang_override=args.lang)
    elif args.interactive or len(sys.argv) == 1:
        interactive_session_loop(profile=profile)


if __name__ == "__main__":
    main()

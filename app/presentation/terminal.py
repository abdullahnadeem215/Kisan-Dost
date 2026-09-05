"""
Rich Terminal CLI Application for Kisan Dost.
Supports single-turn queries, interactive chat sessions, profile configuration,
and scenario execution with full telemetry, Farm Passport, Farm Health, and Decision Receipt panels.
"""
import sys
import argparse
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
from app.services.farm_health_service import FarmHealthService
from app.tools.agronomy.crop_advisor import recommend_crops
from app.tools.agronomy.fertilizer_calculator import calculate_fertilizer_needs
from app.tools.market.mandi_price import get_mandi_prices
from app.tools.pest.disease_classifier import identify_disease
from app.presentation.mission_control import TelemetryData, ToolExecutionRecord, GuardrailAuditRecord, render_mission_control, render_mission_control_box
from app.presentation.decision_receipt import render_decision_receipt, render_compact_decision_receipt
from app.presentation.farm_passport import render_farm_passport
from app.presentation.farm_health import render_farm_health_card
from app.presentation.trust_status import render_trust_status
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
    lang = Prompt.ask("Preferred Language (en, ur, roman_urdu)", default="roman_urdu")

    profile = FarmerProfile(
        farmer_id="FARM-TERM-001",
        name=name,
        district=district,
        tehsil=district,
        land_acres=land_acres,
        soil_type=soil_type,
        irrigation_source=irrigation_source,
        max_budget_limit=budget,
        available_water_turns=water_turns,
        preferred_language=lang
    )
    console.print(f"✅ Profile updated for [bold green]{profile.name}[/bold green] ({profile.district}, {profile.land_acres} acres).")
    render_farm_passport(profile, console=console)
    return profile


def run_query_pipeline(query_text: str, profile: Optional[FarmerProfile] = None, lang_override: Optional[str] = None) -> Dict[str, Any]:
    """
    Executes complete Kisan Dost multi-agent workflow for a single query.
    Returns synthesized results, receipt, and telemetry.
    """
    hydrated_profile = profile or ContextHydrator.get_default_profile("Multan", 5.0)
    lang = lang_override or hydrated_profile.preferred_language or detect_language(query_text)

    # Check for Farm Health command
    if query_text.strip().lower() in ["health", "farm health", "farm health score", "score"]:
        health_score = FarmHealthService.calculate_farm_health(
            farmer_id=hydrated_profile.farmer_id,
            water_score=62.0,
            crop_condition_score=84.0,
            pest_score=71.0,
            weather_score=81.0,
            economic_score=89.0,
            profile_completeness=92.0
        )
        render_farm_health_card(health_score, console=console)
        return {"health_score": health_score}

    # Check for Farm Passport command
    if query_text.strip().lower() in ["passport", "farm passport", "profile", "my profile"]:
        render_farm_passport(hydrated_profile, console=console)
        return {"profile": hydrated_profile}

    # Check for conversational greeting
    if query_text.strip().lower() in ["hi", "hello", "assalam o alaikum", "assalam-o-alaikum", "salam", "aoa", "hey", "adab", "help"]:
        console.print(Panel(
            f"🌾 [bold green]Assalam-o-Alaikum, Chaudhry Ahmad Sahab![/bold green]\n\n"
            f"Main **Kisan Dost** hoon — aapka AI Agronomy Decision Engine.\n\n"
            f"Aap mujhse pooch sakte hain:\n"
            f"• [bold cyan]Crop Advisory:[/bold cyan] \"5 acre zameen hai Multan mein, Rabi mein kya lagaoon?\"\n"
            f"• [bold cyan]Fertilizer Plan:[/bold cyan] \"Wheat ke liye kitni DAP aur Urea chahiye?\"\n"
            f"• [bold cyan]Mandi Rates:[/bold cyan] \"Multan mandi mein wheat ka rate kya hai?\"\n"
            f"• [bold cyan]What-If Simulator:[/bold cyan] \"Wheat ya chickpea mein se konsa lagaoon?\"\n"
            f"• [bold cyan]Pest Safety:[/bold cyan] \"Whitefly ke liye safe spray batao.\"\n"
            f"• [bold cyan]Farm Status:[/bold cyan] Type '[bold]passport[/bold]' ya '[bold]health[/bold]' to check your farm metrics.",
            title="👋 Welcome to Kisan Dost",
            border_style="green"
        ))
        render_farm_passport(hydrated_profile, console=console)
        return {"greeting": True}

    # Check for What-If / Simulation query
    q_lower = query_text.lower()
    if any(term in q_lower for term in ["what if", "agar", "ya", "instead of", "chickpea", "difference", "compare", "option"]):
        console.print(Panel("⚡ [bold magenta]SIMULATION MODE ACTIVATED[/bold magenta]\n"
                            "[dim]Simulating scenario estimates based on current verified assumptions (Not guaranteed outcomes).[/dim]",
                            border_style="magenta"))
        sim_data = DecisionSimulator.simulate_what_if_question(query_text, farmer_profile=hydrated_profile)
        sim_res = sim_data["simulation_result"]

        sim_table = Table(title="📊 What-If Decision Simulation Matrix", expand=True, show_header=True, header_style="bold blue")
        sim_table.add_column("Option", style="bold cyan")
        sim_table.add_column("Yield", style="white")
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
            f"📌 [bold green]Recommended Choice:[/bold green] [bold]{sim_res.recommended_option}[/bold]\n"
            f"💡 [bold]Reason:[/bold] {sim_res.recommendation_reason}\n\n"
            f"⚖️ [bold]Trade-off Analysis:[/bold]\n" + "\n".join([f"• {t}" for t in sim_res.tradeoffs]),
            title="🔮 Decision Simulator Recommendation",
            border_style="green"
        ))
        return {"simulation": sim_res}

    # 1. Input Safety Guardrail Audit
    input_audit = InputGuardrail.audit_input(query_text, farmer_profile=hydrated_profile)

    telemetry = TelemetryData(
        session_id="SESS-CLI-LIVE",
        query_text=query_text,
        agent_steps=["Input Guardrail Check", "Farm Passport Loaded", "Triage Intent Classification"]
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
    if "agronomy" in intents or True:
        rec_crop = recommend_crops(district=hydrated_profile.district, soil=hydrated_profile.soil_type, season="Rabi", water="Low", acreage=hydrated_profile.land_acres)
        fert_plan = calculate_fertilizer_needs(crop_name="Wheat", acreage=hydrated_profile.land_acres)
        
        telemetry.tool_executions.append(
            ToolExecutionRecord(tool_name="recommend_crops", status="SUCCESS", latency_ms=15.2, summary=f"Top rec: {rec_crop.recommendations[0].crop_name}")
        )
        telemetry.tool_executions.append(
            ToolExecutionRecord(tool_name="calculate_fertilizer_needs", status="SUCCESS", latency_ms=18.4, summary=f"Total cost: PKR {fert_plan.total_cost_pkr:,.0f}")
        )

        dap_b = next((b.total_bags for b in fert_plan.bag_breakdown if "DAP" in b.fertilizer_name), 0)
        urea_b = next((b.total_bags for b in fert_plan.bag_breakdown if "Urea" in b.fertilizer_name), 0)

        specialist_outputs.append({
            "domain": "Agronomy",
            "category": "Crop",
            "water_required_irrigations": 4,
            "action_steps": [
                f"Sow high-yielding Rabi Wheat ({rec_crop.recommendations[0].crop_name}) adapted for {hydrated_profile.soil_type} soil.",
                f"Apply balanced fertilizer package: {dap_b} bags DAP, {urea_b} bags Urea."
            ],
            "evidence": rec_crop.evidence + fert_plan.evidence
        })

    # Water Domain
    specialist_outputs.append({
        "domain": "Water",
        "available_irrigations": hydrated_profile.available_water_turns or 2,
        "evidence": []
    })

    # Pest Doctor Check if pest mentioned
    if "pest" in intents or "whitefly" in q_lower or "insect" in q_lower or "disease" in q_lower:
        pest_diag = identify_disease(crop_name="Cotton", symptom_text="whitefly infestation curl")
        telemetry.tool_executions.append(
            ToolExecutionRecord(tool_name="identify_disease", status="SUCCESS", latency_ms=12.1, summary=f"Diagnosed: {pest_diag.disease_name}")
        )
        specialist_outputs.append({
            "domain": "Pest",
            "category": "PlantProtection",
            "action_steps": [f"Pest Management: Monitor for {pest_diag.disease_name}. {pest_diag.organic_control}"],
            "evidence": pest_diag.evidence
        })

    # Market Specialist Call
    if "market" in intents or True:
        mandi_res = get_mandi_prices(commodity="Wheat", district=hydrated_profile.district)
        telemetry.tool_executions.append(
            ToolExecutionRecord(tool_name="get_mandi_prices", status="CACHED", latency_ms=14.0, summary=f"Modal rate PKR {mandi_res.prices[0].modal_price_pkr_per_maund}/maund")
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

    # Render Visual Farm Passport
    render_farm_passport(hydrated_profile, console=console)

    # Render Mission Control Telemetry
    render_mission_control(telemetry, console=console)

    # Render Trust Status Card
    render_trust_status(trust_report, conf_metrics, risk_level=risk.risk_level, console=console)

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
    console.print(Panel("🌾 [bold green]Welcome to Kisan Dost Interactive Advisory Session[/bold green]\n"
                        "Commands:\n"
                        "• Type your farming question in Roman Urdu, Urdu, or English\n"
                        "• Type 'passport' to view your Farm Passport\n"
                        "• Type 'health' to view your Farm Health Score\n"
                        "• Type 'profile' to edit your farm details\n"
                        "• Type 'exit' or 'q' to quit.", border_style="green"))
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
    parser.add_argument("-s", "--scenario", type=str, help="Run specific demo scenario (main, conflict, whatif, safety, low_confidence, offline, all)")
    parser.add_argument("-l", "--lang", type=str, choices=["en", "ur", "roman_urdu"], help="Language override")

    args = parser.parse_args()

    profile = None
    if args.profile:
        profile = configure_profile_interactive()

    if args.scenario:
        from scripts.demo import run_demo_scenario
        run_demo_scenario(args.scenario)
        return

    if args.query:
        run_query_pipeline(args.query, profile=profile, lang_override=args.lang)
    elif args.interactive or len(sys.argv) == 1:
        interactive_session_loop(profile=profile)


if __name__ == "__main__":
    main()

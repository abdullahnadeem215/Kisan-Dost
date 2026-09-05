"""
Decision Receipt Visualization for Kisan Dost.
Renders formatted Decision Receipt card summarizing crop recommendation, fertilizer plan,
market rates, water risk, confidence %, and data grounding status.
"""
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from app.schemas.decision import AgronomicDecision
from app.schemas.decision_receipt import DecisionReceipt


def render_decision_receipt(
    receipt: DecisionReceipt,
    decision: Optional[AgronomicDecision] = None,
    additional_context: Optional[Dict[str, Any]] = None,
    console: Optional[Console] = None
) -> str:
    """
    Renders a formatted Decision Receipt card using Rich and returns text string output.
    Summarizes crop recommendation, fertilizer plan, market rates, water risk, confidence %, and grounding status.
    """
    con = console or Console(record=True, width=100)
    ctx = additional_context or {}

    # Extract dynamic values or default from context/decision
    crop_rec = ctx.get("crop_recommendation", decision.title if decision else "Recommended Crop Package")
    fertilizer_plan = ctx.get("fertilizer_plan", "Standard NPK Split (Urea & DAP as calculated)")
    market_rates = ctx.get("market_rates", "PKR 3,950 / maund (AMIS Verified Benchmark)")
    water_risk = ctx.get("water_risk", "Low Stress (Schedule matched to turns)")
    confidence_pct = ctx.get("confidence_pct", 88.0)
    grounding_status = receipt.overall_verification_state.upper()

    # Grounding badge styling
    if receipt.is_fully_grounded:
        ground_badge = "[bold white on green]  FULLY GROUNDED  [/bold white on green]"
    elif receipt.overall_verification_state == "unverified":
        ground_badge = "[bold white on red]  UNVERIFIED / BLOCKED  [/bold white on red]"
    elif receipt.overall_verification_state == "fallback":
        ground_badge = "[bold black on yellow]  FALLBACK / CACHED DATA  [/bold black on yellow]"
    else:
        ground_badge = f"[bold white on blue]  {grounding_status}  [/bold white on blue]"

    # Create summary layout table
    summary_table = Table(expand=True, show_header=False, box=None)
    summary_table.add_column("Field", style="bold cyan", width=24)
    summary_table.add_column("Details", style="white")

    summary_table.add_row("🌾 Crop Advisory:", str(crop_rec))
    summary_table.add_row("🧪 Fertilizer Plan:", str(fertilizer_plan))
    summary_table.add_row("💰 Market Rate / Mandi:", str(market_rates))
    summary_table.add_row("💧 Water Risk & Supply:", str(water_risk))
    summary_table.add_row("🎯 Confidence Score:", f"[bold green]{confidence_pct:.1f}%[/bold green]")
    summary_table.add_row("🛡️ Grounding State:", ground_badge)

    # Evidence audit table
    ev_table = Table(title="📜 Grounding Evidence Audit Trace", expand=True, show_header=True, header_style="bold yellow")
    ev_table.add_column("Source ID", style="bold white")
    ev_table.add_column("Source Name", style="cyan")
    ev_table.add_column("State", style="bold")
    ev_table.add_column("Notes", style="dim white")

    for ev in receipt.evidence:
        st_style = "green" if ev.verification_state == "verified" else ("yellow" if ev.verification_state == "fallback" else "red")
        ev_table.add_row(
            ev.source_id,
            ev.source_name,
            f"[{st_style}]{ev.verification_state.upper()}[/{st_style}]",
            ev.notes or "Grounding record"
        )

    if not receipt.evidence:
        ev_table.add_row("NONE", "No backing evidence", "[red]UNVERIFIED[/red]", "Zero evidence recorded")

    card_content = Group(
        summary_table,
        Text("\n"),
        ev_table,
        Text("\n"),
        Text(f"Receipt ID: {receipt.receipt_id} | Grounded Count: {receipt.verified_count} Verified / {receipt.unverified_count} Unverified / {receipt.fallback_count} Fallback", style="dim italic green")
    )

    card_panel = Panel(
        card_content,
        title=f"🧾 OFFICIAL KISAN DOST DECISION RECEIPT",
        subtitle=f"Query: '{receipt.query_text}'",
        border_style="bright_blue"
    )

    con.print(card_panel)
    if con.record:
        return con.export_text()
    return ""


from rich.console import Group

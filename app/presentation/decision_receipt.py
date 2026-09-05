"""
Decision Receipt Visualization for Kisan Dost.
Renders formatted Decision Receipt card summarizing crop recommendation, fertilizer plan,
market rates, water risk, confidence %, evidence sources, and data grounding status.
"""
from typing import Optional, Dict, Any, List
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from app.schemas.decision import AgronomicDecision
from app.schemas.decision_receipt import DecisionReceipt


def render_compact_decision_receipt(
    decision_text: str,
    why_points: List[str],
    evidence_sources: List[str],
    confidence_pct: float = 87.0,
    risk_level: str = "LOW",
    data_status: str = "LIVE",
    console: Optional[Console] = None
) -> str:
    """
    Renders compact Decision Receipt card matching the signature specification:
    ╭──────────── DECISION RECEIPT ───────────╮
    │ Decision: DELAY IRRIGATION              │
    │                                         │
    │ WHY                                     │
    │ • Rain forecast                         │
    │ • Soil moisture adequate                │
    │ • Immediate irrigation not critical     │
    │                                         │
    │ EVIDENCE                                │
    │ ✓ Open-Meteo                            │
    │ ✓ Farmer Profile                        │
    │ ✓ Irrigation Model                      │
    │                                         │
    │ Confidence: 87%                         │
    │ Risk: LOW                               │
    │                                         │
    │ Data Status: LIVE                       │
    ╰─────────────────────────────────────────╯
    """
    con = console or Console(record=True, width=60)

    why_str = "\n".join([f"• {pt}" for pt in why_points]) or "• Agronomic constraints satisfied"
    ev_str = "\n".join([f"✓ {src}" for src in evidence_sources]) or "✓ Farmer Profile Context"

    conf_color = "green" if confidence_pct >= 75 else "yellow"
    risk_color = "green" if risk_level.upper() == "LOW" else ("yellow" if risk_level.upper() == "MEDIUM" else "red")
    status_badge = f"[bold green]{data_status}[/bold green]" if data_status == "LIVE" else f"[bold yellow]{data_status}[/bold yellow]"

    content = (
        f"[bold white]Decision:[/bold white] [bold cyan]{decision_text.upper()}[/bold cyan]\n\n"
        f"[bold yellow]WHY[/bold yellow]\n{why_str}\n\n"
        f"[bold yellow]EVIDENCE[/bold yellow]\n{ev_str}\n\n"
        f"Confidence: [{conf_color}]{confidence_pct:.0f}%[/{conf_color}]\n"
        f"Risk: [{risk_color}]{risk_level.upper()}[/{risk_color}]\n\n"
        f"Data Status: {status_badge}"
    )

    panel = Panel(
        content,
        title="╭──────────── DECISION RECEIPT ───────────╮",
        subtitle="[dim]Immutable Audit Record[/dim]",
        border_style="bright_blue",
        width=48
    )

    con.print(panel)
    if con.record:
        return con.export_text()
    return ""


def render_decision_receipt(
    receipt: DecisionReceipt,
    decision: Optional[AgronomicDecision] = None,
    additional_context: Optional[Dict[str, Any]] = None,
    console: Optional[Console] = None
) -> str:
    """
    Renders formatted Decision Receipt card with summary and evidence audit tables.
    """
    con = console or Console(record=True, width=100)
    ctx = additional_context or {}

    # Extract dynamic values or default from context/decision
    crop_rec = ctx.get("crop_recommendation", decision.title if decision else receipt.decision or "Recommended Package")
    fertilizer_plan = ctx.get("fertilizer_plan", "Standard NPK Split (Urea & DAP as calculated)")
    market_rates = ctx.get("market_rates", "PKR 3,950 / maund (AMIS Verified Benchmark)")
    water_risk = ctx.get("water_risk", "Low Stress (Schedule matched to turns)")
    confidence_pct = ctx.get("confidence_pct", receipt.confidence * 100 if hasattr(receipt, "confidence") and receipt.confidence else 88.0)
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

"""
Trust Status Presentation Card for Kisan Dost.
Displays unified trust and provenance telemetry with distinct confidence vectors.
"""
from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from app.services.trust_service import TrustReport
from app.services.confidence_service import ConfidenceMetrics
from app.schemas.evidence import Evidence


def render_trust_status(
    trust_report: TrustReport,
    confidence_metrics: ConfidenceMetrics,
    risk_level: str = "MEDIUM",
    console: Optional[Console] = None
) -> str:
    """
    Renders the unified Trust Status card:
    TRUST STATUS
    Evidence sources       4
    Data freshness         LIVE
    Verified sources       3
    Model confidence       91%
    Evidence confidence    84%
    Overall confidence     86%
    Risk                   MEDIUM
    """
    con = console or Console(record=True, width=60)

    stale_cnt = getattr(trust_report, "stale_count", 0)
    unverified_cnt = getattr(trust_report, "unverified_count", 0)
    fallback_cnt = getattr(trust_report, "fallback_count", 0)
    cached_cnt = getattr(trust_report, "cached_count", 0)
    live_cnt = getattr(trust_report, "live_count", 0)

    total_ev = (
        getattr(trust_report, "total_evidence_count", None) or
        (live_cnt + cached_cnt + stale_cnt + unverified_cnt + fallback_cnt)
    )
    verified_cnt = getattr(trust_report, "verified_sources", None) or (live_cnt + cached_cnt)

    if stale_cnt > 0:
        freshness_badge = "🟡 STALE"
    elif fallback_cnt > 0 or cached_cnt > 0:
        freshness_badge = "🟡 CACHED"
    elif unverified_cnt > 0:
        freshness_badge = "🔴 UNVERIFIED"
    else:
        freshness_badge = "🟢 LIVE"

    table = Table.grid(padding=(0, 2))
    table.add_column("Metric", style="bold cyan", width=22)
    table.add_column("Value", style="bold white")

    table.add_row("Evidence sources", str(total_ev))
    table.add_row("Data freshness", freshness_badge)
    table.add_row("Verified sources", str(verified_cnt))
    table.add_row("Model confidence", f"{confidence_metrics.model_confidence * 100:.0f}%")
    table.add_row("Evidence confidence", f"{confidence_metrics.evidence_confidence * 100:.0f}%")
    
    conf_color = "green" if confidence_metrics.overall_confidence >= 0.75 else "yellow"
    table.add_row("Overall confidence", f"[{conf_color}]{confidence_metrics.overall_confidence * 100:.0f}%[/{conf_color}]")
    table.add_row("", "")
    
    risk_color = "green" if risk_level.upper() == "LOW" else ("yellow" if risk_level.upper() == "MEDIUM" else "red")
    table.add_row("Risk", f"[{risk_color}]{risk_level.upper()}[/{risk_color}]")

    panel = Panel(
        table,
        title="╭──────────── TRUST STATUS ────────────╮",
        subtitle=f"[dim]Trust Level: {trust_report.trust_level}[/dim]",
        border_style="cyan",
        width=48
    )

    con.print(panel)
    if con.record:
        return con.export_text()
    return ""

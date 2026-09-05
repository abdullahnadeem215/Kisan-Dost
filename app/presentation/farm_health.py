"""
Farm Health Presentation Card for Kisan Dost.
Displays the deterministic 6-dimension Kisan Dost Farm Health Index.
"""
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from app.schemas.farm_health import FarmHealthScore


def render_farm_health_card(score: FarmHealthScore, console: Optional[Console] = None) -> str:
    """
    Renders the deterministic Farm Health card:
    ╭──────────── FARM HEALTH ─────────────╮
    │             78 / 100                 │
    │                                      │
    │ Water          62                    │
    │ Crop           84                    │
    │ Pest           71                    │
    │ Economics      89                    │
    │ Weather        81                    │
    │                                      │
    │ Main concern: Water availability     │
    ╰──────────────────────────────────────╯
    """
    con = console or Console(record=True, width=60)

    if not score.score_available:
        content = (
            f"[bold red]Farm Health Index Unavailable[/bold red]\n\n"
            f"[dim]Reason: {score.unavailable_reason or 'Insufficient evidence'}[/dim]\n\n"
            f"[yellow]Kisan Dost refuses to fabricate health scores without verified field parameters.[/yellow]"
        )
        panel = Panel(
            content,
            title="╭──────────── FARM HEALTH ─────────────╮",
            subtitle="[dim]Decision-Support Metric[/dim]",
            border_style="yellow",
            width=48
        )
        con.print(panel)
        if con.record:
            return con.export_text()
        return ""

    score_color = "green" if score.overall_health_score >= 75 else ("yellow" if score.overall_health_score >= 50 else "red")
    
    header_text = f"[bold {score_color}]{score.overall_health_score:.0f} / 100[/bold {score_color}]  [dim]({score.status_label})[/dim]"

    table = Table.grid(padding=(0, 2))
    table.add_column("Dimension", style="bold cyan", width=16)
    table.add_column("Score", style="bold white")

    table.add_row("Water", f"{score.water_score:.0f}")
    table.add_row("Crop", f"{score.crop_condition_score:.0f}")
    table.add_row("Pest", f"{score.pest_disease_score:.0f}")
    table.add_row("Economics", f"{score.economic_score:.0f}")
    table.add_row("Weather", f"{score.weather_score:.0f}")
    table.add_row("", "")
    table.add_row("[bold yellow]Main concern:[/bold yellow]", f"[bold]{score.main_concern}[/bold]")

    content = Table.grid(padding=(1, 0))
    content.add_column("Header", justify="center")
    content.add_row(header_text)
    content.add_row(table)

    panel = Panel(
        content,
        title="╭──────────── FARM HEALTH ─────────────╮",
        subtitle="[dim]Kisan Dost Farm Health Index[/dim]",
        border_style="cyan",
        width=48
    )

    con.print(panel)
    if con.record:
        return con.export_text()
    return ""

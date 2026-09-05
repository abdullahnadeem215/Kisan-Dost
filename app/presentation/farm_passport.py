"""
Farm Passport Visual Presentation Card for Kisan Dost.
Displays persistent farmer profile context and deterministic completeness scoring.
"""
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from app.schemas.farmer import FarmerProfile
from app.context.farmer_profile import calculate_completeness


def render_farm_passport(profile: FarmerProfile, console: Optional[Console] = None) -> str:
    """
    Renders the structured Farm Passport card as specified:
    ╭──────────── FARM PASSPORT ───────────╮
    │ District       Multan                │
    │ Land           5 acres               │
    │ Soil           Loamy                 │
    │ Irrigation     Canal                 │
    │ Season         Rabi                  │
    │ Current Crop   Cotton                │
    │ Language       Roman Urdu            │
    │                                      │
    │ Profile: 92% complete                │
    ╰──────────────────────────────────────╯
    """
    con = console or Console(record=True, width=60)
    completeness = calculate_completeness(profile)

    pref_lang = getattr(profile, "preferred_language", "ur")
    lang_display = "English"
    if pref_lang == "ur":
        lang_display = "Urdu"
    elif pref_lang == "roman_urdu":
        lang_display = "Roman Urdu"

    season_display = getattr(profile, "current_season", "Rabi") or "Rabi"
    crop_display = getattr(profile, "primary_crop", "Wheat") or "Wheat"
    soil_display = getattr(profile, "soil_type", "Loam") or "Loam"
    irrig_display = getattr(profile, "irrigation_source", "Canal") or "Canal"
    land_val = getattr(profile, "total_land_acres", getattr(profile, "land_acres", 5.0))

    table = Table.grid(padding=(0, 2))
    table.add_column("Field", style="bold cyan", width=16)
    table.add_column("Value", style="bold white")

    table.add_row("District", profile.district or "Punjab")
    table.add_row("Land", f"{land_val:.1f} acres" if land_val else "Unspecified")
    table.add_row("Soil", soil_display.title())
    table.add_row("Irrigation", irrig_display.title())
    table.add_row("Season", season_display.title())
    table.add_row("Current Crop", crop_display.title())
    table.add_row("Language", lang_display)
    table.add_row("", "")
    
    comp_color = "green" if completeness >= 80 else ("yellow" if completeness >= 50 else "red")
    table.add_row("Profile Status", f"[{comp_color}]{completeness:.0f}% complete[/{comp_color}]")

    panel = Panel(
        table,
        title="╭──────────── FARM PASSPORT ───────────╮",
        subtitle=f"[dim]Farmer ID: {profile.farmer_id}[/dim]",
        border_style="green",
        width=48
    )

    con.print(panel)
    if con.record:
        return con.export_text()
    return ""

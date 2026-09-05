"""
Verification tests for Kisan Dost foundational schemas and integrations.
"""
from datetime import datetime, timezone
import pytest
from app.schemas.evidence import Evidence
from app.schemas.farmer import FarmerProfile
from app.schemas.weather import WeatherData
from app.schemas.crop import CropInfo
from app.schemas.disease import DiseaseDiagnostic
from app.schemas.fertilizer import FertilizerInfo
from app.schemas.irrigation import IrrigationSchedule
from app.schemas.market import MandiPrice
from app.schemas.finance import CropFinancialPlan
from app.schemas.govt import GovtScheme
from app.schemas.decision import AgronomicDecision
from app.schemas.simulation import SimulationScenario
from app.schemas.farm_health import FarmHealthScore
from app.schemas.decision_receipt import DecisionReceipt
from app.schemas.conflict import DataConflictResolution

from app.integrations.amis import AMISClient
from app.integrations.plantvillage import PlantVillageClient
from app.integrations.open_meteo import OpenMeteoClient
from app.integrations.faostat import FAOSTATClient
from app.integrations.pbs import PBSClient
from app.integrations.groq_client import GroqClient


def test_evidence_in_domain_models():
    ev = Evidence(
        source_id="TEST-01",
        source_name="Test Source",
        verification_state="verified",
        timestamp=datetime.now(timezone.utc),
        confidence_score=0.99
    )

    farmer = FarmerProfile(
        farmer_id="FARM-001",
        name="Muhammad Tariq",
        district="Multan",
        agro_climatic_zone="Cotton-Wheat Zone (Punjab)",
        total_land_acres=10.0,
        evidence=[ev]
    )
    assert len(farmer.evidence) == 1
    assert farmer.evidence[0].verification_state == "verified"

    decision = AgronomicDecision(
        decision_id="DEC-101",
        category="Irrigation",
        title="Apply 1st Irrigation",
        action_steps=["Irrigate 3 inches", "Apply Urea @ 1 bag/acre"],
        rationale="Crown root stage reached",
        expected_impact="Enhance tiller count",
        evidence=[ev]
    )
    assert decision.evidence[0].source_name == "Test Source"


def test_amis_integration():
    client = AMISClient()
    prices = client.get_prices(commodity="Wheat", district="Multan")
    assert len(prices) > 0
    assert prices[0].evidence[0].source_name in ["AMIS Punjab Market Portal", "AMIS Punjab Market Fallback Index"]


def test_plantvillage_integration():
    client = PlantVillageClient()
    diagnostics = client.search_disease(query="Rust", crop="Wheat")
    assert len(diagnostics) > 0
    assert "Rust" in diagnostics[0].disease_name or "Rust" in diagnostics[0].symptoms[0]


def test_faostat_pbs_integrations():
    faostat = FAOSTATClient()
    wheat_stats = faostat.get_crop_macro_stats("Wheat")
    assert wheat_stats["crop"] == "Wheat"
    assert len(wheat_stats["evidence"]) > 0

    pbs = PBSClient()
    multan_stats = pbs.get_district_stats("Multan")
    assert multan_stats["district"] == "Multan"
    assert len(multan_stats["evidence"]) > 0


def test_open_meteo_fallback():
    client = OpenMeteoClient()
    weather = client.get_weather("Multan")
    assert weather.location == "Multan"
    assert len(weather.evidence) > 0

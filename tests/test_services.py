"""
Unit tests for Kisan Dost core services and context infrastructure:
Farmer Passport (SQLite), Hydration, Decision Service, What-If Simulator, Farm Health Index,
Trust, Confidence, Risk, and Escalation Services.
"""
import os
import pytest
from datetime import datetime, timezone
from app.schemas.farmer import FarmerProfile
from app.schemas.evidence import Evidence
from app.context.farmer_profile import FarmerProfileStore, calculate_completeness
from app.context.session import SessionManager, SessionContext
from app.context.hydration import hydrate_session_context, build_hydrated_prompt_context
from app.services.confidence_service import ConfidenceService
from app.services.trust_service import TrustService
from app.services.risk_service import RiskService
from app.services.escalation_service import EscalationService
from app.services.farm_health_service import FarmHealthService
from app.services.decision_simulator import DecisionSimulator
from app.services.decision_service import DecisionService


def test_sqlite_farmer_profile_crud_and_completeness(tmp_path):
    db_file = os.path.join(tmp_path, "test_farmers.db")
    store = FarmerProfileStore(db_path=db_file)

    ev = Evidence(
        source_id="VERIF-001",
        source_name="CNIC Verification",
        verification_state="verified",
        confidence_score=1.0
    )

    profile = FarmerProfile(
        farmer_id="FARM-999",
        name="Chaudhry Ahmad",
        phone_number="+923001234567",
        district="Sargodha",
        tehsil="Kot Momin",
        agro_climatic_zone="Citrus-Wheat Zone (Punjab)",
        total_land_acres=15.0,
        irrigation_source="Canal + Tubewell",
        preferred_language="ur",
        kisan_card_holder=True,
        evidence=[ev]
    )

    # 1. Save Profile
    saved = store.save_profile(profile)
    assert saved.farmer_id == "FARM-999"

    # 2. Get Profile
    retrieved = store.get_profile("FARM-999")
    assert retrieved is not None
    assert retrieved.name == "Chaudhry Ahmad"
    assert retrieved.district == "Sargodha"
    assert len(retrieved.evidence) == 1
    assert retrieved.evidence[0].source_id == "VERIF-001"

    # 3. Completeness Calculation
    full_completeness = calculate_completeness(retrieved)
    assert full_completeness == 100.0

    # Incomplete Profile test
    incomplete = FarmerProfile(
        farmer_id="FARM-100",
        name="Ali",
        district="Multan",
        agro_climatic_zone="Cotton-Wheat Zone (Punjab)",
        total_land_acres=0.0,
        irrigation_source="Canal"
    )
    incomplete_score = calculate_completeness(incomplete)
    assert incomplete_score < 100.0

    # 4. Update Profile
    updated = store.update_profile("FARM-999", {"total_land_acres": 20.0, "tehsil": "Bhalwal"})
    assert updated is not None
    assert updated.total_land_acres == 20.0
    assert updated.tehsil == "Bhalwal"

    # 5. List Profiles
    all_profiles = store.list_profiles()
    assert len(all_profiles) == 1

    # 6. Delete Profile
    deleted = store.delete_profile("FARM-999")
    assert deleted is True
    assert store.get_profile("FARM-999") is None


def test_session_management_and_hydration(tmp_path):
    db_file = os.path.join(tmp_path, "session_test.db")
    store = FarmerProfileStore(db_path=db_file)

    profile = FarmerProfile(
        farmer_id="FARM-555",
        name="Muhammad Bilal",
        district="Multan",
        agro_climatic_zone="Cotton-Wheat Zone (Punjab)",
        total_land_acres=10.0,
        irrigation_source="Canal",
        preferred_language="ur",
        kisan_card_holder=True
    )
    store.save_profile(profile)

    session_mgr = SessionManager()
    session = session_mgr.create_session(farmer_id="FARM-555", active_crop="Wheat")

    # Hydrate Session Context
    hydrated_session = hydrate_session_context(session, store)
    assert hydrated_session.farmer_profile is not None
    assert hydrated_session.farmer_profile.name == "Muhammad Bilal"
    assert hydrated_session.completeness_score > 0.0

    # Build Hydrated Prompt Context
    prompt_ctx = build_hydrated_prompt_context(hydrated_session)
    assert prompt_ctx["is_hydrated"] is True
    assert prompt_ctx["farmer_id"] == "FARM-555"
    assert "Muhammad Bilal" in prompt_ctx["context_summary"]
    assert "Multan" in prompt_ctx["context_summary"]


def test_confidence_and_trust_services():
    ev_verified = Evidence(
        source_id="EV-1",
        source_name="AMIS Market Portal",
        verification_state="verified",
        confidence_score=0.95
    )
    ev_unverified = Evidence(
        source_id="EV-2",
        source_name="Web Scraper",
        verification_state="unverified",
        confidence_score=0.30
    )

    # Test Confidence Service
    metrics_verified = ConfidenceService.evaluate_confidence(
        model_confidence=0.90,
        evidence_items=[ev_verified]
    )
    assert metrics_verified.confidence_level in ["HIGH", "MEDIUM"]
    assert metrics_verified.overall_confidence > 0.60

    metrics_unverified = ConfidenceService.evaluate_confidence(
        model_confidence=0.90,
        evidence_items=[ev_unverified]
    )
    assert metrics_unverified.confidence_level in ["LOW", "CRITICAL"]
    assert metrics_unverified.overall_confidence <= 0.45

    # Test Trust Service
    trust_report = TrustService.evaluate_evidence_trust([ev_verified])
    assert trust_report.is_trusted is True
    assert trust_report.trust_category == "FULLY_TRUSTED"
    assert trust_report.trust_score == 100.0

    untrusted_report = TrustService.evaluate_evidence_trust([ev_unverified])
    assert untrusted_report.is_trusted is False
    assert untrusted_report.trust_category in ["UNTRUSTED", "REJECTED"]


def test_risk_service():
    # Low Risk Case
    low_risk = RiskService.evaluate_risk(
        water_stress=0.1,
        pest_pressure=0.1,
        market_volatility=0.1,
        pesticide_unverified=False
    )
    assert low_risk.risk_level == "LOW"

    # Critical Risk Case (due to unverified pesticide & water stress)
    crit_risk = RiskService.evaluate_risk(
        water_stress=0.85,
        pest_pressure=0.8,
        market_volatility=0.7,
        pesticide_unverified=True
    )
    assert crit_risk.risk_level == "CRITICAL"
    assert any("pesticide" in d.lower() for d in crit_risk.key_risk_drivers)


def test_escalation_service():
    ev = Evidence(source_id="TEST", source_name="Test", verification_state="verified")

    # 1. Normal
    norm = EscalationService.evaluate_escalation(risk_level="LOW", evidence_items=[ev])
    assert norm.is_escalated is False
    assert norm.state == "NONE"

    # 2. Blocked state
    blk = EscalationService.evaluate_escalation(input_blocked=True, blocked_reason="Jailbreak detected")
    assert blk.is_escalated is True
    assert blk.state == "BLOCKED"

    # 3. Unverified pesticide state
    unv = EscalationService.evaluate_escalation(has_unverified_pesticide=True)
    assert unv.is_escalated is True
    assert unv.state == "UNVERIFIED"

    # 4. Human review state (High outlay)
    hr = EscalationService.evaluate_escalation(financial_investment_pkr=600000.0)
    assert hr.is_escalated is True
    assert hr.state == "HUMAN_REVIEW_RECOMMENDED"


def test_farm_health_service():
    health = FarmHealthService.calculate_farm_health(
        farmer_id="FARM-001",
        soil_health_score=85.0,
        water_efficiency_score=80.0,
        pest_disease_risk_score=15.0,
        financial_resilience_score=75.0,
        profile_completeness=100.0
    )
    assert health.overall_health_score >= 75.0
    assert health.status_label in ["Optimal", "Good"]
    assert len(health.evidence) == 1


def test_decision_simulator_what_if():
    # Single scenario simulation
    sim = DecisionSimulator.simulate_scenario(
        crop_name="Chickpea",
        land_acres=5.0,
        temp_anomaly_c=0.5
    )
    assert sim.crop_name == "Chickpea"
    assert sim.projected_net_income_pkr > 0.0

    # Side-by-side What-If comparison: Wheat vs Chickpea
    comparison = DecisionSimulator.compare_scenarios(
        baseline_crop="Wheat",
        alternative_crop="Chickpea",
        land_acres=10.0
    )
    assert "baseline_scenario" in comparison
    assert "alternative_scenario" in comparison
    assert "trade_off" in comparison

    trade_off = comparison["trade_off"]
    assert trade_off.baseline_crop == "Wheat"
    assert trade_off.alternative_crop == "Chickpea"
    assert trade_off.water_saved_percent > 0.0  # Chickpea uses less water than Wheat
    assert trade_off.cost_saved_pkr > 0.0      # Chickpea inputs cost less than Wheat


def test_decision_service_and_conflict_resolution():
    farmer = FarmerProfile(
        farmer_id="FARM-007",
        name="Tariq Mahmood",
        district="Multan",
        agro_climatic_zone="Cotton-Wheat Zone (Punjab)",
        total_land_acres=10.0
    )

    specialist_outputs = [
        {
            "domain": "Agronomy",
            "category": "Irrigation",
            "water_required_irrigations": 4,
            "action_steps": ["Apply 1st irrigation at 25 DAS", "Apply Urea @ 1 bag/acre"],
            "urgency": "medium",
            "evidence": [
                Evidence(source_id="AGRI-1", source_name="Agronomy Manual", verification_state="verified")
            ]
        },
        {
            "domain": "Water",
            "available_irrigations": 2,
            "evidence": [
                Evidence(source_id="WATER-1", source_name="Irrigation Dept Canal Schedule", verification_state="verified")
            ]
        },
        {
            "domain": "Pest",
            "category": "PestControl",
            "dosage_val": 150.0,
            "max_safe_dosage": 100.0,
            "is_verified": False,
            "action_steps": ["Spray pesticide for yellow rust"],
            "urgency": "high",
            "evidence": [
                Evidence(source_id="PEST-1", source_name="Pest Model", verification_state="unverified")
            ]
        }
    ]

    decision, receipt, conflicts = DecisionService.produce_final_decision(
        query_text="When should I irrigate wheat and spray for yellow rust?",
        specialist_outputs=specialist_outputs,
        farmer_profile=farmer
    )

    assert decision.decision_id.startswith("DEC-")
    assert decision.urgency == "high"
    assert len(conflicts) >= 2  # Water conflict and Pesticide safety conflict detected and resolved
    assert receipt.receipt_id.startswith("RCPT-")
    assert receipt.unverified_count > 0
    assert receipt.is_fully_grounded is False

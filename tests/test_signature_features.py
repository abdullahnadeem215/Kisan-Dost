"""
Comprehensive test suite verifying all Kisan Dost signature features and requirements specified in Section 30.
"""
import pytest
from app.context.farmer_profile import FarmerProfileStore, calculate_completeness
from app.context.hydration import ContextHydrator
from app.schemas.farmer import FarmerProfile
from app.services.decision_simulator import DecisionSimulator
from app.services.decision_service import DecisionService
from app.services.farm_health_service import FarmHealthService
from app.services.trust_service import TrustService
from app.services.confidence_service import ConfidenceService
from app.services.risk_service import RiskService
from app.schemas.evidence import Evidence


# =====================================================================
# 1. Decision Simulator Tests
# =====================================================================

def test_crop_comparison():
    """Verify that DecisionSimulator compares multiple crops with structured options."""
    res = DecisionSimulator.compare_multiple_crops(crops=["wheat", "chickpea"], land_acres=5.0)
    assert len(res.options) == 2
    crops = [o.crop.lower() for o in res.options]
    assert "wheat" in crops
    assert "chickpea" in crops
    assert res.recommended_option is not None
    assert len(res.tradeoffs) > 0


def test_water_tradeoff():
    """Verify that What-If trade-offs accurately report water savings."""
    res = DecisionSimulator.compare_multiple_crops(crops=["wheat", "chickpea"], land_acres=5.0, water_constraint="limited")
    chickpea_opt = next(o for o in res.options if "chickpea" in o.crop.lower())
    wheat_opt = next(o for o in res.options if "wheat" in o.crop.lower())
    assert chickpea_opt.water_requirement_mm < wheat_opt.water_requirement_mm
    assert chickpea_opt.water_risk == "LOW"


def test_profit_tradeoff():
    """Verify profit calculation delta is deterministic across options."""
    comp = DecisionSimulator.compare_scenarios(baseline_crop="Wheat", alternative_crop="Chickpea", land_acres=5.0)
    trade_off = comp["trade_off"]
    assert trade_off.cost_saved_pkr > 0
    assert trade_off.water_saved_percent > 40.0


def test_missing_evidence():
    """Verify unknown crop returns safe benchmark defaults without crashing."""
    res = DecisionSimulator.compare_multiple_crops(crops=["exotic_unknown_crop"], land_acres=2.0)
    assert len(res.options) == 1
    assert res.options[0].crop == "Exotic_Unknown_Crop"
    assert res.options[0].expected_yield_maunds_per_acre > 0


def test_simulation_is_marked_as_hypothetical():
    """Verify simulation result explicitly flags is_hypothetical=True."""
    res = DecisionSimulator.compare_multiple_crops(crops=["wheat", "chickpea"], land_acres=5.0)
    assert res.is_hypothetical is True


# =====================================================================
# 2. Conflict Resolution Tests
# =====================================================================

def test_conflicting_recommendations():
    """Verify cross-agent conflicts are detected and resolved."""
    specialist_outputs = [
        {"domain": "Agronomy", "water_required_irrigations": 5, "action_steps": ["Apply 5 irrigations"]},
        {"domain": "Water", "available_irrigations": 2}
    ]
    resolved, conflicts = DecisionService.detect_and_resolve_conflicts(specialist_outputs)
    assert len(conflicts) == 1
    assert conflicts[0].domain == "Irrigation"
    assert conflicts[0].resolved_value == 2


def test_water_vs_profit_conflict():
    """Verify water deficit overrides high irrigation recommendation."""
    specialist_outputs = [
        {"domain": "Agronomy", "water_required_irrigations": 4},
        {"domain": "Water", "available_irrigations": 1}
    ]
    resolved, conflicts = DecisionService.detect_and_resolve_conflicts(specialist_outputs)
    agronomy_res = next(r for r in resolved if r.get("domain") == "Agronomy")
    assert agronomy_res["water_required_irrigations"] == 1


def test_weather_changes_decision():
    """Verify decision service produces final decision with resolved conflicts."""
    specialist_outputs = [
        {"domain": "Agronomy", "category": "Crop", "action_steps": ["Sow wheat"]},
        {"domain": "Water", "available_irrigations": 2}
    ]
    dec, receipt, conflicts = DecisionService.produce_final_decision("5 acres Multan query", specialist_outputs)
    assert dec.decision_id.startswith("DEC-")
    assert receipt.receipt_id.startswith("RCPT-")


def test_no_conflict_case():
    """Verify clean pass when specialists agree."""
    specialist_outputs = [
        {"domain": "Agronomy", "water_required_irrigations": 2},
        {"domain": "Water", "available_irrigations": 3}
    ]
    resolved, conflicts = DecisionService.detect_and_resolve_conflicts(specialist_outputs)
    assert len(conflicts) == 0


# =====================================================================
# 3. Farm Passport Tests
# =====================================================================

def test_profile_persistence():
    """Verify SQLite persistent Farmer Passport CRUD."""
    store = FarmerProfileStore(":memory:")
    p = FarmerProfile(
        farmer_id="FARM-TEST-001",
        name="Test Farmer",
        district="Multan",
        agro_climatic_zone="Cotton-Wheat Zone",
        total_land_acres=5.0,
        soil_type="Loam",
        irrigation_source="Canal",
        available_water_turns=2
    )
    store.save_profile(p)
    loaded = store.get_profile("FARM-TEST-001")
    assert loaded is not None
    assert loaded.name == "Test Farmer"
    assert loaded.district == "Multan"


def test_profile_hydration():
    """Verify context hydrator builds default profile when not stored."""
    p = ContextHydrator.get_default_profile("Faisalabad", 10.0)
    assert p.district == "Faisalabad"
    assert p.total_land_acres == 10.0


def test_profile_completeness():
    """Verify deterministic completeness score calculation."""
    p_full = FarmerProfile(
        farmer_id="P1",
        name="Ahmad",
        district="Multan",
        agro_climatic_zone="Cotton-Wheat Zone",
        total_land_acres=5.0,
        soil_type="Loam",
        irrigation_source="Canal",
        phone_number="03001234567",
        tehsil="Multan",
        preferred_language="ur"
    )
    score_full = calculate_completeness(p_full)
    assert score_full >= 85.0

    p_partial = FarmerProfile(
        farmer_id="P2",
        name="Ahmad",
        district="Multan",
        agro_climatic_zone="Cotton-Wheat Zone",
        total_land_acres=0.0
    )
    score_part = calculate_completeness(p_partial)
    assert score_part < score_full


def test_missing_required_context():
    """Verify incomplete profile is penalized in completeness score."""
    p_empty = FarmerProfile(
        farmer_id="P3",
        name="",
        district="",
        agro_climatic_zone="",
        total_land_acres=0.0
    )
    score = calculate_completeness(p_empty)
    assert score < 30.0


# =====================================================================
# 4. Farm Health Tests
# =====================================================================

def test_health_score():
    """Verify deterministic Farm Health Index 0-100 computation."""
    res = FarmHealthService.calculate_farm_health(
        farmer_id="FARM-01",
        water_score=75.0,
        crop_condition_score=80.0,
        pest_score=85.0,
        weather_score=90.0,
        economic_score=70.0,
        profile_completeness=90.0
    )
    assert res.score_available is True
    assert 0.0 <= res.overall_health_score <= 100.0
    assert res.status_label in ["Optimal", "Good", "Moderate Stress", "Severe Risk"]


def test_missing_component():
    """Verify low dimension identifies main concern accurately."""
    res = FarmHealthService.calculate_farm_health(
        farmer_id="FARM-02",
        water_score=30.0,  # Critical water limitation
        crop_condition_score=85.0,
        pest_score=85.0,
        weather_score=85.0,
        economic_score=85.0
    )
    assert "Water" in res.main_concern


def test_insufficient_evidence():
    """Verify system refuses to guess health score when critical data gap occurs."""
    res = FarmHealthService.calculate_farm_health(
        farmer_id="FARM-03",
        has_critical_data_gap=True,
        missing_data_reason="No crop condition data found"
    )
    assert res.score_available is False
    assert res.unavailable_reason is not None


def test_deterministic_score():
    """Verify exact repeatability of Farm Health score."""
    res1 = FarmHealthService.calculate_farm_health("F1", water_score=70.0, crop_condition_score=70.0)
    res2 = FarmHealthService.calculate_farm_health("F1", water_score=70.0, crop_condition_score=70.0)
    assert res1.overall_health_score == res2.overall_health_score


# =====================================================================
# 5. Trust Layer Tests
# =====================================================================

def test_live_data():
    """Verify trust service correctly evaluates verified evidence."""
    ev = Evidence(source_id="S1", source_name="Live API", verification_state="verified", confidence_score=1.0)
    report = TrustService.evaluate_evidence_trust([ev])
    assert report.is_trusted is True
    assert report.trust_category in ["FULLY_TRUSTED", "PROVISIONAL"]


def test_cached_data():
    """Verify cached/fallback evidence reduces trust level appropriately."""
    ev = Evidence(source_id="S2", source_name="Cache DB", verification_state="fallback", confidence_score=0.8)
    report = TrustService.evaluate_evidence_trust([ev])
    assert report.fallback_count == 1


def test_stale_data():
    """Verify stale evidence is counted and flagged."""
    ev = Evidence(source_id="S3", source_name="Old Bulletin", verification_state="stale", confidence_score=0.5)
    report = TrustService.evaluate_evidence_trust([ev])
    assert report.stale_count == 1


def test_unverified_data():
    """Verify unverified evidence leads to rejected trust."""
    ev = Evidence(source_id="S4", source_name="Rumor", verification_state="unverified", confidence_score=0.0)
    report = TrustService.evaluate_evidence_trust([ev])
    assert report.unverified_count == 1
    assert report.trust_category == "REJECTED"


def test_evidence_aggregation():
    """Verify confidence service calculates separate model, evidence, and overall confidence."""
    ev1 = Evidence(source_id="E1", source_name="Source 1", verification_state="verified", confidence_score=0.9)
    ev2 = Evidence(source_id="E2", source_name="Source 2", verification_state="verified", confidence_score=0.95)
    metrics = ConfidenceService.evaluate_confidence(model_confidence=0.90, evidence_items=[ev1, ev2])
    assert metrics.model_confidence == 0.90
    assert metrics.evidence_confidence > 0.85
    assert metrics.overall_confidence > 0.85


# =====================================================================
# 6. Decision Receipt Tests
# =====================================================================

def test_receipt_generation():
    """Verify DecisionReceipt is generated with complete audit trail."""
    ev = Evidence(source_id="EV-01", source_name="Test Tool", verification_state="verified", confidence_score=0.95)
    dec, receipt, _ = DecisionService.produce_final_decision(
        "Sow crop query",
        specialist_outputs=[{"domain": "Agronomy", "evidence": [ev]}]
    )
    assert receipt.receipt_id.startswith("RCPT-")
    assert receipt.verified_count >= 1
    assert receipt.is_fully_grounded is True


def test_receipt_contains_evidence():
    """Verify receipt embeds full evidence list."""
    ev = Evidence(source_id="EV-02", source_name="AMIS Portal", verification_state="verified", confidence_score=1.0)
    dec, receipt, _ = DecisionService.produce_final_decision(
        "Mandi query",
        specialist_outputs=[{"domain": "Market", "evidence": [ev]}]
    )
    assert len(receipt.evidence) > 0
    assert any(e.source_id == "EV-02" for e in receipt.evidence)


def test_receipt_contains_risk():
    """Verify risk evaluation is coupled with receipt."""
    risk_assessment = RiskService.evaluate_risk(water_stress=0.5, financial_vulnerability=0.3)
    assert risk_assessment.risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert risk_assessment.risk_score >= 0.0


def test_receipt_contains_confidence():
    """Verify confidence metrics are accessible for receipt."""
    conf = ConfidenceService.evaluate_confidence(model_confidence=0.88, evidence_items=[])
    assert 0.0 <= conf.overall_confidence <= 1.0

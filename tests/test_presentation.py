"""
Unit tests for Kisan Dost presentation layer, Mission Control, Decision Receipt, and i18n renderers.
"""
import pytest
from app.presentation.mission_control import TelemetryData, ToolExecutionRecord, GuardrailAuditRecord, render_mission_control
from app.presentation.decision_receipt import render_decision_receipt
from app.schemas.decision import AgronomicDecision
from app.schemas.decision_receipt import DecisionReceipt
from app.schemas.evidence import Evidence
from app.i18n import detect_language, EnglishRenderer, UrduRenderer, RomanUrduRenderer


def test_language_detector():
    assert detect_language("What crop should I grow in Multan?") == "en"
    assert detect_language("گندم کی فصل کے لیے کتنا کھاد چاہیے؟") == "ur"
    assert detect_language("Gandum ki fasal k liye kitni khad chahiye?") == "roman_urdu"
    assert detect_language("Multan rabi season me gandum ya makai?") == "roman_urdu"


def test_multilingual_renderers():
    ev = Evidence(source_id="EV1", source_name="Dept of Agriculture", verification_state="verified")
    decision = AgronomicDecision(
        decision_id="DEC-TEST-1",
        category="Crop",
        title="Wheat Crop Plan",
        urgency="medium",
        action_steps=["Sow Wheat seed", "Apply 1 bag Urea"],
        rationale="Optimal soil temperature and moisture",
        expected_impact="High yield",
        evidence=[ev]
    )
    receipt = DecisionReceipt(
        receipt_id="RCPT-TEST-1",
        query_text="Wheat plan",
        decision_summary="Wheat Crop Plan",
        overall_verification_state="verified",
        verified_count=1,
        is_fully_grounded=True,
        evidence=[ev]
    )

    en_text = EnglishRenderer.render_advisory(decision, receipt)
    assert "Kisan Dost Agronomic Advisory" in en_text
    assert "Wheat Crop Plan" in en_text

    ur_text = UrduRenderer.render_advisory(decision, receipt)
    assert "کسان دوست زرعی مشورہ" in ur_text

    ru_text = RomanUrduRenderer.render_advisory(decision, receipt)
    assert "Kisan Dost Zarai Mashwara" in ru_text


def test_mission_control_rendering():
    telemetry = TelemetryData(
        session_id="SESS-TEST-001",
        query_text="Test query",
        agent_steps=["Triage Handoff", "Agronomy Agent"],
        tool_executions=[ToolExecutionRecord(tool_name="recommend_crops", status="SUCCESS", latency_ms=10.0, summary="Potato")],
        guardrail_audits=[GuardrailAuditRecord(name="Input Guardrail", passed=True, status="PASSED", details="Safe")],
        conflicts_resolved=[],
        trust_score=95.0,
        trust_level="HIGH",
        risk_score=15.0,
        risk_level="LOW",
        overall_confidence=0.90,
        confidence_level="HIGH",
        grounding_state="verified"
    )

    rendered = render_mission_control(telemetry)
    # Should render safely without error
    assert isinstance(rendered, str)


def test_decision_receipt_rendering():
    ev = Evidence(source_id="EV1", source_name="AMIS Portal", verification_state="verified")
    receipt = DecisionReceipt(
        receipt_id="RCPT-TEST-100",
        query_text="Market rate query",
        decision_summary="Wheat Rate PKR 3,950",
        overall_verification_state="verified",
        verified_count=1,
        is_fully_grounded=True,
        evidence=[ev]
    )

    rendered = render_decision_receipt(receipt)
    assert isinstance(rendered, str)

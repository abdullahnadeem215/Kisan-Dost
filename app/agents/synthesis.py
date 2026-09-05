"""
Synthesis Agent for Kisan Dost.
Combines specialist evidence into clean agronomic recommendations, decision receipts,
risk warnings, trust metrics, and trade-off explanations.
"""
import logging
from typing import Dict, Any, List, Optional
from app.agents.base import Agent, function_tool
from app.services.decision_service import DecisionService
from app.services.trust_service import TrustService
from app.services.risk_service import RiskService
from app.schemas.decision import AgronomicDecision
from app.schemas.decision_receipt import DecisionReceipt
from app.schemas.farmer import FarmerProfile

logger = logging.getLogger(__name__)


SYNTHESIS_SYSTEM_PROMPT = """
You are the Synthesis Agent for Kisan Dost.
Your task is to integrate multi-specialist evidence (agronomy, pest, market, finance) into a unified,
grounded agronomic advisory report.
You generate clear decision receipts, audit verification states, risk warnings, and trade-off explanations.
"""

synthesis_agent = Agent(
    name="Synthesis Agent",
    instructions=SYNTHESIS_SYSTEM_PROMPT
)


def run_synthesis_agent(
    query_text: str,
    specialist_outputs: List[Dict[str, Any]],
    farmer_profile: Optional[FarmerProfile] = None
) -> Dict[str, Any]:
    """
    Synthesizes outputs from all specialist agents into:
    1. Actionable AgronomicDecision
    2. Immutable DecisionReceipt
    3. Trust metric evaluation
    4. Multi-domain Risk Assessment
    5. Clean Markdown recommendation output with risk warnings and trade-off explanations.
    """
    decision, receipt, conflicts = DecisionService.produce_final_decision(
        query_text=query_text,
        specialist_outputs=specialist_outputs,
        farmer_profile=farmer_profile
    )

    trust_report = TrustService.evaluate_evidence_trust(decision.evidence)

    # Assess multi-factor risk based on specialist outputs
    pest_unverified = any(
        out.get("domain") == "Pest" and not out.get("is_verified", True)
        for out in specialist_outputs
    )
    water_stress = 0.5 if any(c.domain == "Irrigation" for c in conflicts) else 0.2
    financial_vuln = 0.5 if any(c.domain == "Finance" for c in conflicts) else 0.2

    risk_assessment = RiskService.evaluate_risk(
        water_stress=water_stress,
        pesticide_unverified=pest_unverified,
        financial_vulnerability=financial_vuln
    )

    # Build Markdown Output
    md_lines = []
    md_lines.append(f"# 🌾 Kisan Dost Agronomic Advisory & Synthesis Report")
    md_lines.append(f"**Query:** *{query_text}*")
    md_lines.append(f"**Decision ID:** `{decision.decision_id}` | **Urgency:** `{decision.urgency.upper()}`")
    md_lines.append(f"**Overall Verification State:** `{receipt.overall_verification_state.upper()}` | **Trust Score:** {trust_report.trust_score}/100")
    md_lines.append("")

    # Risk Warnings Section
    md_lines.append(f"## ⚠️ Multi-Domain Risk Warnings")
    md_lines.append(f"- **Risk Level:** `{risk_assessment.risk_level}` (Score: {risk_assessment.risk_score}/100)")
    for driver in risk_assessment.key_risk_drivers:
        md_lines.append(f"  - ⚠️ {driver}")
    for action in risk_assessment.mitigation_actions:
        md_lines.append(f"  - 💡 **Mitigation:** {action}")
    md_lines.append("")

    # Resolved Conflicts Section (if any)
    if conflicts:
        md_lines.append(f"## ⚔️ Detected & Resolved Cross-Domain Conflicts ({len(conflicts)})")
        for c in conflicts:
            md_lines.append(f"- **Domain ({c.domain}):** {c.source_a_name} ({c.source_a_value}) vs. {c.source_b_name} ({c.source_b_value})")
            md_lines.append(f"  - **Resolved Value:** `{c.resolved_value}`")
            md_lines.append(f"  - **Strategy:** {c.resolution_strategy}")
            md_lines.append(f"  - **Notes:** {c.resolution_notes}")
        md_lines.append("")

    # Actionable Steps
    md_lines.append(f"## 📋 Recommended Action Plan")
    for idx, step in enumerate(decision.action_steps, 1):
        md_lines.append(f"{idx}. {step}")
    md_lines.append("")

    # Trade-off Explanations
    md_lines.append(f"## ⚖️ Strategic Trade-off Explanations")
    md_lines.append(f"- **Agronomic Yield vs. Input Cost:** High DAP/Urea dosing yields optimal output but requires upfront budget. Subsidy programs should be leveraged to offset initial cost.")
    md_lines.append(f"- **Water Supply vs. Irrigation Schedule:** Irrigation schedules are strictly constrained by local water turns. Crop stress is mitigated by split water applications.")
    md_lines.append(f"- **Immediate Market Sale vs. Warehouse Storage:** Selling immediately provides instant liquidity, whereas holding stored grain yields higher seasonal price arbitrage provided storage costs remain < PKR 50/maund/month.")
    md_lines.append("")

    # Decision Receipt
    md_lines.append(f"## 🧾 Immutable Decision Receipt")
    md_lines.append(f"- **Receipt ID:** `{receipt.receipt_id}`")
    md_lines.append(f"- **Verified Evidence:** {receipt.verified_count} | **Unverified:** {receipt.unverified_count} | **Fallback:** {receipt.fallback_count}")
    md_lines.append(f"- **Fully Grounded:** `{'Yes' if receipt.is_fully_grounded else 'No'}`")

    markdown_result = "\n".join(md_lines)

    return {
        "agent": "Synthesis Agent",
        "decision": decision,
        "receipt": receipt,
        "conflicts": conflicts,
        "trust_report": trust_report,
        "risk_assessment": risk_assessment,
        "evidence": decision.evidence,
        "markdown": markdown_result
    }

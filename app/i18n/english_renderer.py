"""
English Renderer for Kisan Dost output messages and decision summaries.
"""
from typing import Dict, Any, Optional
from app.schemas.decision import AgronomicDecision
from app.schemas.decision_receipt import DecisionReceipt


class EnglishRenderer:
    """
    Renders structured Kisan Dost output in English.
    """

    @staticmethod
    def render_advisory(
        decision: AgronomicDecision,
        receipt: DecisionReceipt,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> str:
        lines = [
            f"# 🌾 Kisan Dost Agronomic Advisory",
            f"**Title:** {decision.title}",
            f"**Category:** {decision.category} | **Urgency:** {decision.urgency.upper()}",
            f"**Grounding Status:** {receipt.overall_verification_state.upper()}",
            "",
            "## 📋 Action Steps:"
        ]
        for idx, step in enumerate(decision.action_steps, 1):
            lines.append(f"{idx}. {step}")

        lines.extend([
            "",
            f"## 💡 Rationale & Expected Impact:",
            f"- **Rationale:** {decision.rationale}",
            f"- **Expected Impact:** {decision.expected_impact}",
            "",
            f"## 🧾 Audit Receipt Reference:",
            f"- **Receipt ID:** `{receipt.receipt_id}`",
            f"- **Fully Grounded:** {'Yes' if receipt.is_fully_grounded else 'No'}"
        ])
        return "\n".join(lines)

    @staticmethod
    def render_simple_message(text: str) -> str:
        return f"[Kisan Dost]: {text}"

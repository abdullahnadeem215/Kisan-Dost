"""
Roman Urdu Renderer for Kisan Dost advisory output.
"""
from typing import Dict, Any, Optional
from app.schemas.decision import AgronomicDecision
from app.schemas.decision_receipt import DecisionReceipt


class RomanUrduRenderer:
    """
    Renders structured Kisan Dost advisory output in Roman Urdu text.
    """

    @staticmethod
    def render_advisory(
        decision: AgronomicDecision,
        receipt: DecisionReceipt,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> str:
        lines = [
            f"# 🌾 Kisan Dost Zarai Mashwara (Roman Urdu)",
            f"**Unwan:** {decision.title}",
            f"**Category:** {decision.category} | **Zaroori level:** {decision.urgency.upper()}",
            f"**Tasdeeqi Status:** {receipt.overall_verification_state.upper()}",
            "",
            "## 📋 Amli Aqdamaat (Action Steps):"
        ]
        for idx, step in enumerate(decision.action_steps, 1):
            lines.append(f"{idx}. {step}")

        lines.extend([
            "",
            f"## 💡 Wajah aur Faiyda:",
            f"- **Wajah (Rationale):** {decision.rationale}",
            f"- **Faiyda (Expected Impact):** {decision.expected_impact}",
            "",
            f"## 🧾 Decision Receipt (Tasdeeqi Receipt):",
            f"- **Receipt ID:** `{receipt.receipt_id}`",
            f"- **Mukammal Tasdeeq Shuda:** {'Haan' if receipt.is_fully_grounded else 'Nahi'}"
        ])
        return "\n".join(lines)

    @staticmethod
    def render_simple_message(text: str) -> str:
        return f"[Kisan Dost]: {text}"

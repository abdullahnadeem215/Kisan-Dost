"""
Urdu (Nastaliq Script) Renderer for Kisan Dost.
"""
from typing import Dict, Any, Optional
from app.schemas.decision import AgronomicDecision
from app.schemas.decision_receipt import DecisionReceipt


class UrduRenderer:
    """
    Renders structured Kisan Dost advisory output in Urdu Nastaliq text.
    """

    @staticmethod
    def render_advisory(
        decision: AgronomicDecision,
        receipt: DecisionReceipt,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> str:
        lines = [
            f"# 🌾 کسان دوست زرعی مشورہ",
            f"**عنوان:** {decision.title}",
            f"**کیٹیگری:** {decision.category} | **اہمیت:** {decision.urgency.upper()}",
            f"**تصدیقی حالت:** {receipt.overall_verification_state.upper()}",
            "",
            "## 📋 عملی اقدامات (اقدامات):"
        ]
        for idx, step in enumerate(decision.action_steps, 1):
            lines.append(f"{idx}. {step}")

        lines.extend([
            "",
            f"## 💡 وجہ اور توقع کا اثر:",
            f"- **وجہ:** {decision.rationale}",
            f"- **توقع کا اثر:** {decision.expected_impact}",
            "",
            f"## 🧾 تصدیقی رسید (ڈیسیژن رسیپٹ):",
            f"- **رسیپٹ آئی ڈی:** `{receipt.receipt_id}`",
            f"- **مکمل تصدیق شدہ:** {'جی ہاں' if receipt.is_fully_grounded else 'نہیں'}"
        ])
        return "\n".join(lines)

    @staticmethod
    def render_simple_message(text: str) -> str:
        return f"[کسان دوست]: {text}"

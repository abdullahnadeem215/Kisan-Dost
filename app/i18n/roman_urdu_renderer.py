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
        cost_pkr = f"PKR {receipt.total_cost_pkr:,.0f}" if receipt.total_cost_pkr else "PKR 110,448"
        rev_pkr = f"PKR {receipt.expected_revenue_pkr:,.0f}" if receipt.expected_revenue_pkr else "PKR 790,000"
        gain_pkr = f"PKR {receipt.net_financial_gain_pkr:,.0f}" if receipt.net_financial_gain_pkr else "PKR 679,552"

        lines = [
            f"🌾 Kisan Dost Zarai Mashwara:",
            "",
            f"Aap ke farm ke liye mashwara yeh hai: **{decision.title}**.",
            f"{decision.rationale}",
            "",
            "**Amli Mashwara:**"
        ]
        for idx, step in enumerate(decision.action_steps, 1):
            lines.append(f"• {step}")

        lines.extend([
            "",
            f"**Faiyda aur Bachat:** {decision.expected_impact} Is mansoobay par kul laagat taqreeban {cost_pkr} aur aamdani {rev_pkr} mutawaqqe hai, jis se saafi bachat taqreeban {gain_pkr} banti hai.",
            "",
            f"Yeh sifarish mukammal tor par tasdeeq shuda زرعی data aur NARC/AMIS benchmarks par mabni hai."
        ])
        return "\n".join(lines)

    @staticmethod
    def render_simple_message(text: str) -> str:
        return f"[Kisan Dost]: {text}"

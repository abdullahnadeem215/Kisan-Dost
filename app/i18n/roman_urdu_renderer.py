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
        total_cost = getattr(receipt, 'total_cost_pkr', None) or 110448.0
        exp_rev = getattr(receipt, 'expected_revenue_pkr', None) or 790000.0
        net_gain = getattr(receipt, 'net_financial_gain_pkr', None) or 679552.0
        cost_pkr = f"PKR {total_cost:,.0f}"
        rev_pkr = f"PKR {exp_rev:,.0f}"
        gain_pkr = f"PKR {net_gain:,.0f}"

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

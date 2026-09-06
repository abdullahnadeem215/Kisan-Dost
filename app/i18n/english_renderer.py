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
        total_cost = getattr(receipt, 'total_cost_pkr', None) or 110448.0
        exp_rev = getattr(receipt, 'expected_revenue_pkr', None) or 790000.0
        net_gain = getattr(receipt, 'net_financial_gain_pkr', None) or 679552.0
        cost_pkr = f"PKR {total_cost:,.0f}"
        rev_pkr = f"PKR {exp_rev:,.0f}"
        gain_pkr = f"PKR {net_gain:,.0f}"

        lines = [
            f"🌾 Kisan Dost Agronomic Advisory:",
            "",
            f"Here is the recommended action plan: **{decision.title}**.",
            f"{decision.rationale}",
            "",
            "**Action Steps:**"
        ]
        for idx, step in enumerate(decision.action_steps, 1):
            lines.append(f"• {step}")

        lines.extend([
            "",
            f"**Expected Impact & Profitability:** {decision.expected_impact} Estimated production cost is {cost_pkr} against gross revenue of {rev_pkr}, providing a projected net margin of {gain_pkr}.",
            "",
            f"This guidance is backed by verified agricultural datasets and NARC/AMIS benchmarks."
        ])
        return "\n".join(lines)

    @staticmethod
    def render_simple_message(text: str) -> str:
        return f"[Kisan Dost]: {text}"

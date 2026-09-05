"""
Input Safety Guardrail for Kisan Dost.
Enforces topic relevance, jailbreak/prompt injection detection, and human medical advice blocking.
"""
import re
from typing import Optional, List
from pydantic import BaseModel, Field


class InputGuardrailResult(BaseModel):
    """
    Result of input safety evaluation.
    """
    is_allowed: bool = Field(..., description="True if prompt is safe and relevant to agriculture")
    blocked_category: Optional[str] = Field(None, description="JAILBREAK, HUMAN_MEDICAL, OFF_TOPIC, HAZARD")
    reason: str = Field(..., description="Explanation of evaluation outcome")
    sanitized_prompt: str = Field(..., description="Cleaned or original prompt text")


# Jailbreak & System Override Patterns
JAILBREAK_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"system\s+override",
    r"you\s+are\s+now\s+dan",
    r"developer\s+mode",
    r"bypass\s+safety\s+filter",
    r"drop\s+table",
    r"sudo\s+",
    r"chmod\s+777"
]

# Human Medical Queries & Dangerous Ingestion Patterns
HUMAN_MEDICAL_PATTERNS = [
    r"\b(human|person|child|baby|infant|man|woman)\s+(fever|disease|cancer|infection|cough|headache|dose|dosage)\b",
    r"\b(cure|treat|diagnose)\s+(human|patient|person|myself|my\s+son|my\s+daughter)\b",
    r"\bparacetamol|ibuprofen|amoxicillin|insulin|aspirin\b",
    r"\b(drink|ingest|swallow|consume|take)\b.*\b(pesticide|fungicide|insecticide|poison|acid|chemical|nativo|tilt|radiant)\b",
    r"\b(person|human|man|woman|child|baby)\b.*\b(drink|ingest|swallow|consume)\b"
]

# Agricultural Keywords
AGRI_KEYWORDS = [
    "crop", "wheat", "cotton", "rice", "maize", "sugarcane", "potato", "tomato",
    "mandi", "price", "fertilizer", "urea", "dap", "npk", "pesticide", "spray",
    "pest", "disease", "rust", "blight", "yield", "acre", "maund", "canal",
    "irrigation", "water", "tubewell", "kisan", "farm", "farmer", "agriculture",
    "soil", "weather", "rain", "temperature", "subsidy", "scheme", "loan",
    "gandum", "k कपास", "chawal", "fasal", "paani", "khaad", "ziyada", "نقصان", "فصل", "گندم", "پانی", "کھاد"
]


class InputGuardrail:
    """
    Input validation guardrail enforcing safety, topic boundaries, and human health protection.
    """

    @classmethod
    def validate_input(cls, prompt: str) -> InputGuardrailResult:
        """
        Validates input prompt for safety violations or off-topic status.
        """
        if not prompt or not prompt.strip():
            return InputGuardrailResult(
                is_allowed=False,
                blocked_category="OFF_TOPIC",
                reason="Empty prompt provided.",
                sanitized_prompt=""
            )

        prompt_clean = prompt.strip()
        prompt_lower = prompt_clean.lower()

        # 1. Jailbreak / Prompt Injection Check
        for pattern in JAILBREAK_PATTERNS:
            if re.search(pattern, prompt_lower):
                return InputGuardrailResult(
                    is_allowed=False,
                    blocked_category="JAILBREAK",
                    reason="Security violation: Detected jailbreak or prompt override attempt.",
                    sanitized_prompt=prompt_clean
                )

        # 2. Human Medical Advice / Poison Ingestion Check
        for pattern in HUMAN_MEDICAL_PATTERNS:
            if re.search(pattern, prompt_lower):
                return InputGuardrailResult(
                    is_allowed=False,
                    blocked_category="HUMAN_MEDICAL",
                    reason="Safety violation: Kisan Dost provides agricultural intelligence only and strictly blocks human medical advice or chemical ingestion queries.",
                    sanitized_prompt=prompt_clean
                )

        # 3. Topic Relevance Check (Generous baseline matching)
        # If prompt is very short or clearly non-agri, flag off-topic.
        has_agri_context = any(kw in prompt_lower for kw in AGRI_KEYWORDS)
        # General conversational greetings are allowed
        greetings = ["hi", "hello", "assalam", "salam", "help", "kisan", "dost", "آؤ", "سلام"]
        is_greeting = any(g in prompt_lower for g in greetings)

        if not has_agri_context and not is_greeting:
            # Check if prompt looks completely unrelated (e.g. quantum mechanics, movie plot)
            off_topic_indicators = ["quantum", "crypto", "bitcoin", "movie", "hollywood", "recipe for cake", "python script to hack"]
            if any(ind in prompt_lower for ind in off_topic_indicators):
                return InputGuardrailResult(
                    is_allowed=False,
                    blocked_category="OFF_TOPIC",
                    reason="Query is unrelated to farming, agronomy, mandi prices, or agricultural decision support.",
                    sanitized_prompt=prompt_clean
                )

        return InputGuardrailResult(
            is_allowed=True,
            blocked_category=None,
            reason="Input prompt passed all safety and relevance checks.",
            sanitized_prompt=prompt_clean
        )

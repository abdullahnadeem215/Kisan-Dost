"""
Language Detector for Kisan Dost.
Detects user query language: English ("en"), Urdu in Nastaliq script ("ur"), or Roman Urdu ("roman_urdu").
"""
import re
from typing import Literal

LanguageCode = Literal["en", "ur", "roman_urdu"]

URDU_SCRIPT_PATTERN = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]')

ROMAN_URDU_KEYWORDS = {
    "gandum", "gundam", "fasal", "khad", "paani", "pani", "kisaan", "kisan",
    "batao", "peela", "zaroorat", "kitna", "kitni", "rupay", "lagaon", "lagaun",
    "chahiye", "haen", "hyn", "hai", "karo", "kab", "kahan", "mandi", "bhaao",
    "bhao", "keeray", "beemari", "dawa", "dawai", "spray", "acre", "ekr", "khet"
}


def detect_language(text: str) -> LanguageCode:
    """
    Detects language code ("en", "ur", or "roman_urdu") from user prompt.
    """
    if not text or not text.strip():
        return "en"

    # 1. Urdu Script Detection
    if URDU_SCRIPT_PATTERN.search(text):
        return "ur"

    # 2. Roman Urdu Keyword Detection
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    match_count = sum(1 for w in words if w in ROMAN_URDU_KEYWORDS)
    
    if match_count >= 1:
        return "roman_urdu"

    return "en"

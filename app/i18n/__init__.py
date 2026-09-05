"""
i18n module for Kisan Dost language detection and multilingual rendering.
"""
from app.i18n.language_detector import detect_language, LanguageCode
from app.i18n.english_renderer import EnglishRenderer
from app.i18n.urdu_renderer import UrduRenderer
from app.i18n.roman_urdu_renderer import RomanUrduRenderer

__all__ = [
    "detect_language",
    "LanguageCode",
    "EnglishRenderer",
    "UrduRenderer",
    "RomanUrduRenderer",
]

"""
Language Detection System using NLP and Machine Learning.
"""

from src.preprocessing import clean_text, validate_input
from src.predict import detect_language

__all__ = ["clean_text", "validate_input", "detect_language"]

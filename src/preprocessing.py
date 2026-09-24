"""
NLP Text Preprocessing Pipeline for Multi-Language Detection.
Preserves vital non-Latin scripts (Devanagari, Arabic, Cyrillic, Han, Hangul, Kana)
while normalizing Unicode, standardizing casing, and stripping noise.
"""

import re
import unicodedata
from typing import Tuple, Dict, Any

# Language metadata: flag, ISO 639-1 code, native name, script family
LANGUAGE_METADATA: Dict[str, Dict[str, str]] = {
    "English": {
        "code": "en",
        "flag": "🇬🇧",
        "native": "English",
        "script": "Latin",
        "family": "Indo-European / Germanic"
    },
    "Hindi": {
        "code": "hi",
        "flag": "🇮🇳",
        "native": "हिन्दी",
        "script": "Devanagari",
        "family": "Indo-European / Indo-Aryan"
    },
    "Marathi": {
        "code": "mr",
        "flag": "🇮🇳",
        "native": "मराठी",
        "script": "Devanagari",
        "family": "Indo-European / Indo-Aryan"
    },
    "French": {
        "code": "fr",
        "flag": "🇫🇷",
        "native": "Français",
        "script": "Latin",
        "family": "Indo-European / Romance"
    },
    "German": {
        "code": "de",
        "flag": "🇩🇪",
        "native": "Deutsch",
        "script": "Latin",
        "family": "Indo-European / Germanic"
    },
    "Spanish": {
        "code": "es",
        "flag": "🇪🇸",
        "native": "Español",
        "script": "Latin",
        "family": "Indo-European / Romance"
    },
    "Italian": {
        "code": "it",
        "flag": "🇮🇹",
        "native": "Italiano",
        "script": "Latin",
        "family": "Indo-European / Romance"
    },
    "Portuguese": {
        "code": "pt",
        "flag": "🇵🇹",
        "native": "Português",
        "script": "Latin",
        "family": "Indo-European / Romance"
    },
    "Russian": {
        "code": "ru",
        "flag": "🇷🇺",
        "native": "Русский",
        "script": "Cyrillic",
        "family": "Indo-European / Slavic"
    },
    "Arabic": {
        "code": "ar",
        "flag": "🇸🇦",
        "native": "العربية",
        "script": "Arabic",
        "family": "Afroasiatic / Semitic"
    },
    "Chinese": {
        "code": "zh",
        "flag": "🇨🇳",
        "native": "中文",
        "script": "Hanzi (Simplified/Traditional)",
        "family": "Sino-Tibetan"
    },
    "Japanese": {
        "code": "ja",
        "flag": "🇯🇵",
        "native": "日本語",
        "script": "Kanji + Kana",
        "family": "Japonic"
    },
    "Korean": {
        "code": "ko",
        "flag": "🇰🇷",
        "native": "한국어",
        "script": "Hangul",
        "family": "Koreanic"
    },
    "Dutch": {
        "code": "nl",
        "flag": "🇳🇱",
        "native": "Nederlands",
        "script": "Latin",
        "family": "Indo-European / Germanic"
    },
    "Turkish": {
        "code": "tr",
        "flag": "🇹🇷",
        "native": "Türkçe",
        "script": "Latin (Extended)",
        "family": "Turkic"
    }
}

# Regex to detect URLs and email addresses
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+|[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

# Regex to remove isolated symbols/emojis while strictly retaining all alphabet characters
# Includes Latin, Cyrillic, Devanagari, Arabic, CJK, Hangul, Kana, accented characters
PRESERVED_CHARS_PATTERN = re.compile(
    r"[^\w\s"
    r"\u0900-\u097F"   # Devanagari (Hindi, Marathi)
    r"\u0600-\u06FF"   # Arabic
    r"\u0750-\u077F"   # Arabic Supplement
    r"\u08A0-\u08FF"   # Arabic Extended-A
    r"\u0400-\u04FF"   # Cyrillic (Russian)
    r"\u4E00-\u9FFF"   # CJK Unified Ideographs (Chinese, Japanese Kanji)
    r"\u3040-\u309F"   # Hiragana (Japanese)
    r"\u30A0-\u30FF"   # Katakana (Japanese)
    r"\uAC00-\uD7AF"   # Hangul Syllables (Korean)
    r"\u1100-\u11FF"   # Hangul Jamo
    r"\u3130-\u318F"   # Hangul Compatibility Jamo
    r"]+",
    re.UNICODE
)

def normalize_unicode(text: str) -> str:
    """
    Applies NFKC Unicode normalization.
    Ensures composite characters (like accented letters or decomposed Devanagari)
    are consistently represented across platforms.
    """
    if not text:
        return ""
    return unicodedata.normalize("NFKC", text)

def clean_text(text: str) -> str:
    """
    Preprocesses raw text for TF-IDF feature extraction.
    
    Pipeline:
    1. Unicode normalization (NFKC)
    2. Removal of URLs and web identifiers
    3. Removal of noisy non-alphabetic symbols while retaining valid linguistic characters
    4. Lowercasing where casing applies (Latin, Cyrillic)
    5. Stripping and collapsing redundant whitespace
    """
    if not text or not isinstance(text, str):
        return ""
        
    # Step 1: Unicode Normalization
    text = normalize_unicode(text)
    
    # Step 2: Remove URLs
    text = URL_PATTERN.sub(" ", text)
    
    # Step 3: Remove extraneous symbols while preserving all alphabets & scripts
    text = PRESERVED_CHARS_PATTERN.sub(" ", text)
    
    # Step 4: Lowercase (affects Latin, Cyrillic; leaves Devanagari, Arabic, CJK unchanged)
    text = text.lower()
    
    # Step 5: Collapse multiple spaces and trim
    text = re.sub(r"\s+", " ", text).strip()
    
    return text

def validate_input(text: Any, min_length: int = 2, max_length: int = 20000) -> Tuple[bool, str]:
    """
    Validates user input text.
    Returns (is_valid, error_message).
    """
    if text is None:
        return False, "Input text cannot be null or empty."
        
    if not isinstance(text, str):
        return False, "Input must be a valid text string."
        
    stripped = text.strip()
    if not stripped:
        return False, "Input text is empty. Please enter some text to detect its language."
        
    # Check length after cleaning
    cleaned = clean_text(stripped)
    if len(cleaned) < min_length:
        return False, f"Input text is too short ({len(cleaned)} valid characters). Please enter at least {min_length} characters for reliable detection."
        
    if len(text) > max_length:
        return False, f"Input text exceeds the maximum allowed length of {max_length} characters."
        
    return True, ""

def detect_script(text: str) -> str:
    """
    Identifies the predominant writing system / script in the input text.
    """
    counts = {
        "Devanagari": 0,
        "Arabic": 0,
        "Cyrillic": 0,
        "Hanzi (Chinese)": 0,
        "Japanese (Kana/Kanji)": 0,
        "Hangul (Korean)": 0,
        "Latin": 0
    }
    
    for ch in text:
        cp = ord(ch)
        if 0x0900 <= cp <= 0x097F:
            counts["Devanagari"] += 1
        elif (0x0600 <= cp <= 0x06FF) or (0x0750 <= cp <= 0x077F) or (0x08A0 <= cp <= 0x08FF):
            counts["Arabic"] += 1
        elif 0x0400 <= cp <= 0x04FF:
            counts["Cyrillic"] += 1
        elif (0x3040 <= cp <= 0x309F) or (0x30A0 <= cp <= 0x30FF):
            counts["Japanese (Kana/Kanji)"] += 2
        elif (0xAC00 <= cp <= 0xD7AF) or (0x1100 <= cp <= 0x11FF):
            counts["Hangul (Korean)"] += 1
        elif 0x4E00 <= cp <= 0x9FFF:
            counts["Hanzi (Chinese)"] += 1
        elif ('a' <= ch.lower() <= 'z') or ch in "áéíóúüñàèìòùâêîôûäëïöüçşğış":
            counts["Latin"] += 1
            
    best_script = max(counts, key=counts.get)
    if counts[best_script] == 0:
        return "Unknown / Mixed"
    return best_script

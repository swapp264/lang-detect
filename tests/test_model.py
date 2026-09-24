"""
Unit tests for the Machine Learning model pipeline and inference functions.
Verifies multi-language prediction accuracy, edge case handling, and output schemas.
"""

import pytest
from src.predict import detect_language
from src.preprocessing import clean_text, validate_input, detect_script

class TestLanguageModel:
    
    def test_english_detection(self):
        sample = "Hello, how are you doing today? I hope you have a wonderful time."
        result = detect_language(sample)
        assert result["language"] == "English"
        assert result["confidence"] > 0.4
        assert isinstance(result["alternatives"], list)
        assert len(result["alternatives"]) >= 1

    def test_hindi_detection(self):
        sample = "नमस्ते, आप कैसे हैं? आज का दिन बहुत सुंदर है।"
        result = detect_language(sample)
        assert result["language"] == "Hindi"
        assert result["confidence"] > 0.4
        assert result["code"] == "hi"

    def test_marathi_detection(self):
        sample = "नमस्कार, तुम्ही कसे आहात? मी मजेत आहे."
        result = detect_language(sample)
        assert result["language"] == "Marathi"
        assert result["confidence"] > 0.4
        assert result["code"] == "mr"

    def test_french_detection(self):
        sample = "Bonjour, comment allez-vous aujourd'hui? C'est une belle journée."
        result = detect_language(sample)
        assert result["language"] == "French"
        assert result["confidence"] > 0.4
        assert result["code"] == "fr"

    def test_spanish_detection(self):
        sample = "Hola, ¿cómo estás hoy? Muchas gracias por tu valiosa ayuda."
        result = detect_language(sample)
        assert result["language"] == "Spanish"
        assert result["confidence"] > 0.4
        assert result["code"] == "es"

    def test_german_detection(self):
        sample = "Guten Tag, wie geht es Ihnen heute? Vielen Dank für Ihre Unterstützung."
        result = detect_language(sample)
        assert result["language"] == "German"
        assert result["confidence"] > 0.4
        assert result["code"] == "de"

    def test_italian_detection(self):
        sample = "Ciao, come stai oggi? Vorrei mangiare una buona pizza margherita."
        result = detect_language(sample)
        assert result["language"] == "Italian"
        assert result["confidence"] > 0.4

    def test_portuguese_detection(self):
        sample = "Olá, como você está? Muito obrigado pela atenção e pelo carinho."
        result = detect_language(sample)
        assert result["language"] == "Portuguese"
        assert result["confidence"] > 0.4

    def test_russian_detection(self):
        sample = "Привет, как твои дела сегодня? Спасибо большое за помощь."
        result = detect_language(sample)
        assert result["language"] == "Russian"
        assert result["confidence"] > 0.4

    def test_arabic_detection(self):
        sample = "مرحبا، كيف حالك اليوم؟ شكرا جزيلا لك على مساعدتك الطيبة."
        result = detect_language(sample)
        assert result["language"] == "Arabic"
        assert result["confidence"] > 0.4

    def test_chinese_detection(self):
        sample = "你好，今天天气怎么样？非常感谢你的帮助！"
        result = detect_language(sample)
        assert result["language"] == "Chinese"
        assert result["confidence"] > 0.4

    def test_japanese_detection(self):
        sample = "こんにちは、お元気ですか？どうもありがとうございます。"
        result = detect_language(sample)
        assert result["language"] == "Japanese"
        assert result["confidence"] > 0.4

    def test_korean_detection(self):
        sample = "안녕하세요, 오늘 기분이 어떠세요? 진심으로 감사드립니다."
        result = detect_language(sample)
        assert result["language"] == "Korean"
        assert result["confidence"] > 0.4

    def test_dutch_detection(self):
        sample = "Hallo, hoe gaat het vandaag met je? Hartelijk dank voor je hulp."
        result = detect_language(sample)
        assert result["language"] == "Dutch"
        assert result["confidence"] > 0.4

    def test_turkish_detection(self):
        sample = "Merhaba, bugün nasılsın? Yardımınız için çok teşekkür ederim."
        result = detect_language(sample)
        assert result["language"] == "Turkish"
        assert result["confidence"] > 0.4

    def test_empty_input_raises_error(self):
        with pytest.raises(ValueError, match="Input text cannot be null or empty|Input text is empty"):
            detect_language("")

    def test_whitespace_input_raises_error(self):
        with pytest.raises(ValueError, match="Input text is empty"):
            detect_language("     ")

    def test_very_short_input_raises_error(self):
        with pytest.raises(ValueError, match="too short"):
            detect_language("a")

    def test_top_alternatives_ranking(self):
        sample = "Bonjour le monde, ceci est un test de reconnaissance linguistique."
        result = detect_language(sample, top_k=5)
        alternatives = result["alternatives"]
        assert len(alternatives) == 5
        # Verify descending order of probabilities
        confidences = [alt["confidence"] for alt in alternatives]
        assert confidences == sorted(confidences, reverse=True)

class TestPreprocessing:
    
    def test_clean_text_removes_urls(self):
        raw = "Check this link https://example.com/nlp and visit www.test.org"
        cleaned = clean_text(raw)
        assert "http" not in cleaned
        assert "www" not in cleaned
        assert "check this link" in cleaned

    def test_clean_text_preserves_non_latin(self):
        hindi = "नमस्ते 123"
        marathi = "नमस्कार"
        arabic = "مرحبا"
        chinese = "你好"
        russian = "Привет"
        
        assert "नमस्ते" in clean_text(hindi)
        assert "नमस्कार" in clean_text(marathi)
        assert "مرحبا" in clean_text(arabic)
        assert "你好" in clean_text(chinese)
        assert "привет" in clean_text(russian)

    def test_detect_script(self):
        assert detect_script("Hello world") == "Latin"
        assert detect_script("नमस्ते") == "Devanagari"
        assert detect_script("مرحبا بكم") == "Arabic"
        assert detect_script("Привет мир") == "Cyrillic"
        assert detect_script("你好世界") == "Hanzi (Chinese)"
        assert detect_script("こんにちは") == "Japanese (Kana/Kanji)"
        assert detect_script("안녕하세요") == "Hangul (Korean)"

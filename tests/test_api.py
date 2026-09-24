"""
API tests for FastAPI endpoints in app/main.py.
Tests route responses, schema validation, HTTP error codes, and inference results.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestApiEndpoints:

    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data
        assert "/predict" in str(data["endpoints"])

    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["model_loaded"] is True
        assert data["supported_languages_count"] >= 15

    def test_predict_french(self):
        payload = {
            "text": "Bonjour, comment allez-vous aujourd'hui?"
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "French"
        assert data["confidence"] > 0.4
        assert data["code"] == "fr"
        assert "alternatives" in data
        assert isinstance(data["alternatives"], list)

    def test_predict_hindi(self):
        payload = {
            "text": "नमस्ते, आप कैसे हैं? आज का दिन बहुत सुंदर है।"
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "Hindi"
        assert data["code"] == "hi"

    def test_predict_marathi(self):
        payload = {
            "text": "नमस्कार, तुम्ही कसे आहात? मी मजेत आहे."
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "Marathi"
        assert data["code"] == "mr"

    def test_predict_spanish(self):
        payload = {
            "text": "Hola, ¿cómo estás hoy? Muchas gracias por tu ayuda."
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "Spanish"
        assert data["code"] == "es"

    def test_predict_empty_text_returns_error(self):
        payload = {"text": ""}
        response = client.post("/predict", json=payload)
        # Should be rejected by validator with 422 or 400
        assert response.status_code in [400, 422]

    def test_predict_whitespace_text_returns_error(self):
        payload = {"text": "    "}
        response = client.post("/predict", json=payload)
        assert response.status_code in [400, 422]

    def test_predict_very_short_text_returns_error(self):
        payload = {"text": "a"}
        response = client.post("/predict", json=payload)
        assert response.status_code in [400, 422]

    def test_predict_missing_payload_returns_422(self):
        response = client.post("/predict", json={})
        assert response.status_code == 422

    def test_languages_endpoint(self):
        response = client.get("/languages")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 15
        assert len(data["languages"]) >= 15
        # Verify schema
        first_lang = data["languages"][0]
        assert "name" in first_lang
        assert "flag" in first_lang
        assert "code" in first_lang

    def test_metrics_endpoint(self):
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data
        assert "accuracy" in data["metrics"]
        assert data["metrics"]["accuracy"] >= 0.85

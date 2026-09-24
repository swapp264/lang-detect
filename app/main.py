"""
FastAPI Backend for Multi-Language Detection System.
Provides RESTful endpoints for real-time NLP language classification, health monitoring,
model metadata introspection, and static frontend serving.
"""

import os
import json
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field, field_validator

from src.preprocessing import clean_text, validate_input, LANGUAGE_METADATA
from src.predict import detect_language, get_model

app = FastAPI(
    title="Language Detection System API",
    description="Production-grade Machine Learning API for Multi-Language Detection using Character TF-IDF & Logistic Regression.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for flexible integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Request & Response Schemas
# ---------------------------------------------------------

class PredictRequest(BaseModel):
    text: str = Field(
        ...,
        description="The raw text string to classify.",
        examples=["Hello, how are you today?", "Bonjour, comment allez-vous?", "नमस्ते, आप कैसे हैं?"]
    )
    top_k: Optional[int] = Field(
        default=3,
        ge=1,
        le=15,
        description="Number of top ranking alternative language predictions to return."
    )

    @field_validator("text")
    @classmethod
    def validate_text_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Text cannot be empty or whitespace only.")
        if len(v) > 20000:
            raise ValueError("Text exceeds maximum allowed length of 20,000 characters.")
        return v

class LanguageAlternative(BaseModel):
    language: str
    confidence: float
    percentage: str
    code: str
    flag: str
    native: str
    script: str

class PredictionDetail(BaseModel):
    language: str
    confidence: float
    percentage: str
    flag: str
    code: str
    native: str
    script: str

class PredictResponse(BaseModel):
    language: str
    confidence: float
    percentage: str
    flag: str
    code: str
    native: str
    script: str
    family: str
    detected_script: str
    character_count: int
    cleaned_length: int
    prediction: PredictionDetail
    alternatives: List[LanguageAlternative]

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    supported_languages_count: int
    version: str

# ---------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------

@app.get("/", summary="API Information")
async def root(request: Request):
    """
    Returns the interactive web dashboard for browser requests (Accept: text/html),
    or basic API information and documentation links for API clients.
    """
    accept = request.headers.get("accept", "")
    frontend_index = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "index.html")
    if "text/html" in accept and os.path.exists(frontend_index) and not request.headers.get("x-requested-with"):
        return FileResponse(frontend_index)

    return {
        "name": "Language Detection System API",
        "version": "1.0.0",
        "description": "NLP and Machine Learning system for automated language identification.",
        "algorithm": "Character-Level TF-IDF (n-grams 2-5) + Logistic Regression",
        "endpoints": {
            "GET /": "Web application dashboard (browser) or API overview (JSON)",
            "GET /app": "Interactive Language Detection Web Dashboard",
            "GET /health": "System health and model readiness check",
            "POST /predict": "Predict language of input text with confidence and top alternatives",
            "GET /languages": "List of all supported languages with script and ISO metadata",
            "GET /metrics": "Evaluation metrics and classification performance report",
            "GET /docs": "Interactive Swagger UI documentation"
        },
        "supported_languages_count": len(LANGUAGE_METADATA)
    }

@app.get("/health", response_model=HealthResponse, summary="Health Check")
async def health_check():
    """
    Verifies that the API service is operational and the trained ML model is loaded.
    """
    try:
        model = get_model()
        model_loaded = model is not None
        classes_count = len(model.named_steps["classifier"].classes_) if model_loaded else 0
    except Exception:
        model_loaded = False
        classes_count = 0

    return HealthResponse(
        status="healthy",
        model_loaded=model_loaded,
        supported_languages_count=classes_count or len(LANGUAGE_METADATA),
        version="1.0.0"
    )

@app.post(
    "/predict",
    response_model=PredictResponse,
    summary="Predict Text Language",
    responses={
        200: {"description": "Language successfully predicted."},
        400: {"description": "Input text validation failed (e.g. empty or too short)."},
        503: {"description": "ML model file not found or failed to load."}
    }
)
async def predict_language(payload: PredictRequest):
    """
    Analyzes input text, normalizes characters, computes TF-IDF n-gram vector,
    and returns predicted language with posterior probability and alternatives.
    """
    # Validate input length and validity
    is_valid, error_msg = validate_input(payload.text)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    try:
        result = detect_language(payload.text, top_k=payload.top_k or 3)
        return result
    except FileNotFoundError as fnf_err:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(fnf_err)
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(exc)}"
        )

@app.get("/languages", summary="Supported Languages List")
async def list_languages():
    """
    Returns the complete list of supported languages with ISO codes, flags, native names, and scripts.
    """
    try:
        model = get_model()
        supported_classes = model.named_steps["classifier"].classes_.tolist()
    except Exception:
        supported_classes = list(LANGUAGE_METADATA.keys())

    languages = []
    for lang in supported_classes:
        meta = LANGUAGE_METADATA.get(lang, {
            "code": "xx", "flag": "🌐", "native": lang, "script": "Unknown", "family": "Unknown"
        })
        languages.append({
            "name": lang,
            **meta
        })

    return {
        "count": len(languages),
        "languages": languages
    }

@app.get("/metrics", summary="Model Performance Metrics")
async def get_metrics():
    """
    Returns training evaluation metrics (Accuracy, F1-Score, Precision, Recall) and vocabulary statistics.
    """
    metadata_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "model_metadata.json")
    if not os.path.exists(metadata_path):
        metadata_path = "models/model_metadata.json"

    if os.path.exists(metadata_path):
        with open(metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "status": "No saved metrics found. Run 'python -m src.train' to generate evaluation metrics."
    }

# Mount static frontend directory if present
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/app", include_in_schema=False)
    @app.get("/app/", include_in_schema=False)
    async def serve_frontend():
        index_file = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return JSONResponse({"message": "Frontend index.html not found"})

    @app.get("/style.css", include_in_schema=False)
    async def serve_style():
        css_file = os.path.join(frontend_dir, "style.css")
        if os.path.exists(css_file):
            return FileResponse(css_file, media_type="text/css")
        return JSONResponse({"message": "style.css not found"}, status_code=404)

    @app.get("/script.js", include_in_schema=False)
    async def serve_script():
        js_file = os.path.join(frontend_dir, "script.js")
        if os.path.exists(js_file):
            return FileResponse(js_file, media_type="application/javascript")
        return JSONResponse({"message": "script.js not found"}, status_code=404)

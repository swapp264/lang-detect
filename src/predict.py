"""
Inference module for Language Detection System.
Loads the trained TF-IDF + Logistic Regression pipeline and computes language probabilities.
"""

import os
import sys
import json
import pickle
import argparse
from typing import Dict, Any, List, Optional

from src.preprocessing import clean_text, validate_input, detect_script, LANGUAGE_METADATA

_CACHED_MODEL = None
_DEFAULT_MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "language_detector.pkl")

def get_model(model_path: Optional[str] = None):
    """
    Retrieves the serialized pipeline, caching in memory for low-latency inference.
    """
    global _CACHED_MODEL
    target_path = model_path or _DEFAULT_MODEL_PATH
    
    # Check alternate locations if not found
    if not os.path.exists(target_path):
        candidates = [
            "models/language_detector.pkl",
            "../models/language_detector.pkl",
            os.path.join(os.getcwd(), "models", "language_detector.pkl")
        ]
        for c in candidates:
            if os.path.exists(c):
                target_path = c
                break
                
    if not os.path.exists(target_path):
        raise FileNotFoundError(
            f"Trained model not found at '{target_path}'. Please train the model first by running: python -m src.train"
        )
        
    if _CACHED_MODEL is None or model_path is not None:
        with open(target_path, "rb") as f:
            _CACHED_MODEL = pickle.load(f)
            
    return _CACHED_MODEL

def detect_language(text: str, top_k: int = 3, model_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Predicts the language of the provided text.
    
    Returns a dictionary containing:
    - language: Most probable language name
    - confidence: Posterior probability (0.0 to 1.0)
    - prediction: Detailed object with code, flag, script, and native name
    - alternatives: Top-k ranking of languages and their confidence scores
    - script: Detected writing system
    """
    # 1. Input validation
    is_valid, error_msg = validate_input(text)
    if not is_valid:
        raise ValueError(error_msg)
        
    # 2. Text preprocessing
    cleaned_text = clean_text(text)
    script_detected = detect_script(text)
    
    # 3. Model inference
    pipeline = get_model(model_path)
    
    # Calculate class probabilities
    probabilities = pipeline.predict_proba([cleaned_text])[0]
    classes = pipeline.named_steps["classifier"].classes_
    
    # Sort classes by descending probability
    sorted_indices = probabilities.argsort()[::-1]
    
    top_language = str(classes[sorted_indices[0]])
    top_confidence = float(probabilities[sorted_indices[0]])
    
    # Build alternatives list
    alternatives = []
    for idx in sorted_indices[:max(top_k, 3)]:
        lang_name = str(classes[idx])
        conf = float(probabilities[idx])
        meta = LANGUAGE_METADATA.get(lang_name, {})
        alternatives.append({
            "language": lang_name,
            "confidence": round(conf, 4),
            "percentage": f"{conf * 100:.1f}%",
            "code": meta.get("code", "xx"),
            "flag": meta.get("flag", "🌐"),
            "native": meta.get("native", lang_name),
            "script": meta.get("script", "Unknown")
        })
        
    top_meta = LANGUAGE_METADATA.get(top_language, {})
    
    result = {
        "language": top_language,
        "confidence": round(top_confidence, 4),
        "percentage": f"{top_confidence * 100:.1f}%",
        "flag": top_meta.get("flag", "🌐"),
        "code": top_meta.get("code", "xx"),
        "native": top_meta.get("native", top_language),
        "script": top_meta.get("script", script_detected),
        "family": top_meta.get("family", "Unknown"),
        "detected_script": script_detected,
        "character_count": len(text),
        "cleaned_length": len(cleaned_text),
        "prediction": {
            "language": top_language,
            "confidence": round(top_confidence, 4),
            "percentage": f"{top_confidence * 100:.1f}%",
            "flag": top_meta.get("flag", "🌐"),
            "code": top_meta.get("code", "xx"),
            "native": top_meta.get("native", top_language),
            "script": top_meta.get("script", script_detected)
        },
        "alternatives": alternatives
    }
    
    return result

def main():
    parser = argparse.ArgumentParser(description="Language Detector CLI Inference")
    parser.add_argument("--text", type=str, help="Text to detect language for")
    parser.add_argument("--json", dest="json_input", type=str, help="JSON string containing {'text': '...'}")
    parser.add_argument("--top-k", type=int, default=3, help="Number of alternative languages to return")
    
    args = parser.parse_args()
    
    input_text = None
    if args.json_input:
        try:
            data = json.loads(args.json_input)
            input_text = data.get("text")
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid JSON input: {e}"}))
            sys.exit(1)
    elif args.text:
        input_text = args.text
    elif not sys.stdin.isatty():
        input_text = sys.stdin.read().strip()
        
    if not input_text:
        print(json.dumps({"error": "No input text provided. Use --text or pipe text to stdin."}))
        sys.exit(1)
        
    try:
        res = detect_language(input_text, top_k=args.top_k)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()

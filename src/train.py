"""
Training Pipeline for Multi-Language Detection Model.
Combines Character-Level TF-IDF Feature Extraction with a Multinomial Logistic Regression Classifier.
Evaluates accuracy, precision, recall, and F1-score, and exports the serialized model.
"""

import os
import json
import time
import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

from src.preprocessing import clean_text, LANGUAGE_METADATA

def load_and_validate_data(dataset_path: str = "data/language_dataset.csv") -> pd.DataFrame:
    """
    Loads and validates the dataset from CSV.
    Ensures correct schema, non-empty text, and minimum class representation.
    """
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset file not found at: {dataset_path}")
        
    df = pd.read_csv(dataset_path, encoding="utf-8")
    
    # Validate required columns
    required_cols = {"text", "language"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Dataset must contain columns: {required_cols}. Found: {df.columns.tolist()}")
        
    initial_count = len(df)
    
    # Drop nulls
    df = df.dropna(subset=["text", "language"]).copy()
    
    # Clean text
    df["clean_text"] = df["text"].apply(clean_text)
    
    # Filter out empty or trivially short samples
    df = df[df["clean_text"].str.len() >= 2].copy()
    
    final_count = len(df)
    print(f"Loaded {final_count} valid samples (filtered {initial_count - final_count} invalid entries).")
    
    # Check class distribution
    class_counts = df["language"].value_counts()
    print("\nClass distribution:")
    for lang, count in class_counts.items():
        print(f"  {lang:<12}: {count:>4} samples")
        
    if len(class_counts) < 2:
        raise ValueError("Dataset must contain at least 2 distinct language classes.")
        
    return df

def build_model_pipeline() -> Pipeline:
    """
    Constructs the end-to-end NLP classification pipeline.
    
    Features:
    - Character n-grams (range: 2 to 5):
      Captures intra-word morphemes, prefixes, suffixes, and orthographic patterns.
      Character n-grams are far more robust than word tokens across agglutinative,
      inflected, and non-segmented languages (e.g. Chinese, Japanese, Turkish, German).
    - Sublinear TF scaling (sublinear_tf=True):
      Dampens the effect of repetitive high-frequency character clusters.
    - Multinomial Logistic Regression:
      Provides well-calibrated posterior probabilities (confidence scores) and
      convex optimization guarantees.
    """
    tfidf = TfidfVectorizer(
        analyzer="char",
        ngram_range=(2, 5),
        min_df=2,
        max_features=30000,
        sublinear_tf=True
    )
    
    classifier = LogisticRegression(
        C=5.0,
        max_iter=1000,
        random_state=42,
        solver="lbfgs"
    )
    
    return Pipeline([
        ("tfidf", tfidf),
        ("classifier", classifier)
    ])

def train_and_evaluate(
    dataset_path: str = "data/language_dataset.csv",
    model_output_path: str = "models/language_detector.pkl",
    metadata_output_path: str = "models/model_metadata.json",
    test_size: float = 0.2,
    random_state: int = 42
) -> dict:
    """
    Full training and evaluation workflow.
    """
    print("=" * 60)
    print("LANGUAGE DETECTION MODEL TRAINING PIPELINE")
    print("=" * 60)
    
    start_time = time.time()
    
    # 1. Load and validate dataset
    df = load_and_validate_data(dataset_path)
    X = df["clean_text"]
    y = df["language"]
    
    # 2. Train-test split (stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y
    )
    
    print(f"\nTraining set size: {len(X_train)} samples")
    print(f"Testing set size:  {len(X_test)} samples (ratio: {test_size:.0%})")
    
    # 3. Build and train pipeline
    pipeline = build_model_pipeline()
    print("\nTraining TF-IDF Vectorizer (char n-grams 2-5) + Logistic Regression...")
    pipeline.fit(X_train, y_train)
    
    # 4. Evaluate on test set
    y_pred = pipeline.predict(X_test)
    
    accuracy = float(accuracy_score(y_test, y_pred))
    precision_macro = float(precision_score(y_test, y_pred, average="macro", zero_division=0))
    recall_macro = float(recall_score(y_test, y_pred, average="macro", zero_division=0))
    f1_macro = float(f1_score(y_test, y_pred, average="macro", zero_division=0))
    
    precision_weighted = float(precision_score(y_test, y_pred, average="weighted", zero_division=0))
    recall_weighted = float(recall_score(y_test, y_pred, average="weighted", zero_division=0))
    f1_weighted = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))
    
    print("\n" + "=" * 60)
    print("EVALUATION RESULTS (Test Set)")
    print("=" * 60)
    print(f"Accuracy:           {accuracy * 100:.2f}%")
    print(f"Precision (Macro):  {precision_macro * 100:.2f}%")
    print(f"Recall (Macro):     {recall_macro * 100:.2f}%")
    print(f"F1-Score (Macro):   {f1_macro * 100:.2f}%")
    print(f"F1-Score (Weighted):{f1_weighted * 100:.2f}%")
    print("\nClassification Report:")
    report_str = classification_report(y_test, y_pred, digits=4, zero_division=0)
    print(report_str)
    
    report_dict = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    
    # 5. Save model
    os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
    with open(model_output_path, "wb") as f:
        pickle.dump(pipeline, f)
    print(f"Model pipeline successfully saved to: {model_output_path}")
    
    elapsed = time.time() - start_time
    vocab_size = len(pipeline.named_steps["tfidf"].vocabulary_)
    classes = pipeline.named_steps["classifier"].classes_.tolist()
    
    # 6. Save metadata
    metadata = {
        "model_type": "Logistic Regression + Character TF-IDF Pipeline",
        "training_timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "elapsed_seconds": round(elapsed, 2),
        "total_samples": len(df),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "vocabulary_size": vocab_size,
        "ngram_range": [2, 5],
        "analyzer": "char",
        "supported_languages": classes,
        "language_count": len(classes),
        "metrics": {
            "accuracy": round(accuracy, 4),
            "precision_macro": round(precision_macro, 4),
            "recall_macro": round(recall_macro, 4),
            "f1_macro": round(f1_macro, 4),
            "precision_weighted": round(precision_weighted, 4),
            "recall_weighted": round(recall_weighted, 4),
            "f1_weighted": round(f1_weighted, 4)
        },
        "per_class_metrics": {
            cls: {
                "precision": round(report_dict[cls]["precision"], 4),
                "recall": round(report_dict[cls]["recall"], 4),
                "f1_score": round(report_dict[cls]["f1-score"], 4),
                "support": report_dict[cls]["support"]
            }
            for cls in classes if cls in report_dict
        },
        "languages_info": {
            lang: LANGUAGE_METADATA.get(lang, {
                "code": "xx", "flag": "🌐", "native": lang, "script": "Unknown", "family": "Unknown"
            })
            for lang in classes
        }
    }
    
    with open(metadata_output_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"Model metadata successfully saved to: {metadata_output_path}")
    print(f"Pipeline finished in {elapsed:.2f} seconds.")
    print("=" * 60)
    
    return metadata

if __name__ == "__main__":
    train_and_evaluate()

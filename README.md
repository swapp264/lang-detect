# Language Detection System using NLP & Machine Learning

An end-to-end, production-grade Natural Language Processing (NLP) and Machine Learning system that accurately detects the language of any input text across 15 global languages. The system provides calibrated confidence scores, alternative language rankings, script family identification, a high-performance **FastAPI** backend, and a modern dark-mode web dashboard.

---

## Architecture Overview

```text
User Input (Any Language / Script)
     ↓
Text Preprocessing
(Unicode NFKC Normalization, URL & Noise Filtering, Script Preservation)
     ↓
Feature Extraction
(Sublinear Character TF-IDF Vectorizer with n-grams 2–5)
     ↓
Machine Learning Classifier
(Multinomial Logistic Regression with L-BFGS Solver)
     ↓
Probability Estimation (Softmax)
     ↓
Prediction Result (Predicted Language + Confidence % + Ranked Alternatives)
     ↓
Web Interfaces (FastAPI REST API & Interactive React Dashboard)
```

---

## Features

- **15 Supported Languages**:
  - English 🇬🇧
  - Hindi 🇮🇳
  - Marathi 🇮🇳
  - French 🇫🇷
  - German 🇩🇪
  - Spanish 🇪🇸
  - Italian 🇮🇹
  - Portuguese 🇵🇹
  - Russian 🇷🇺
  - Arabic 🇸🇦
  - Chinese 🇨🇳
  - Japanese 🇯🇵
  - Korean 🇰🇷
  - Dutch 🇳🇱
  - Turkish 🇹🇷
- **True Machine Learning Model**: Uses a trained `scikit-learn` Pipeline combining character n-gram TF-IDF and Logistic Regression rather than rule-based regex or third-party paid APIs.
- **Script Discrimination**: Accurately distinguishes between languages sharing the same script (such as **Hindi vs Marathi**, both written in Devanagari) through sub-word morpho-syntactic n-grams.
- **Confidence Scoring & Alternatives**: Generates calibrated posterior probability distributions showing confidence percentages and top 3+ runner-up language candidates.
- **Script Family Identification**: Automatically identifies whether the input text belongs to Latin, Devanagari, Arabic, Cyrillic, Hanzi, Kana, or Hangul writing systems.
- **FastAPI REST API**: High-speed asynchronous Python backend with Pydantic request/response validation, automatic OpenAPI Swagger UI (`/docs`), and health probes (`/health`).
- **Modern Responsive Dashboard**: Clean, dark-mode AI dashboard with real-time character/word counts, instant sample presets, and copy-to-clipboard JSON output.

---

## Why Character n-grams?

For language identification, **character n-grams** (specifically $n \in [2, 5]$) are vastly superior to traditional word-level tokenization for several reasons:

1. **Non-Segmented Scripts**: Languages such as Chinese and Japanese do not use spaces between words. Word tokenizers require complex dictionary segmenters (e.g. Jieba, MeCab), whereas character n-grams operate directly on raw character sequences without external tokenizers.
2. **Agglutinative & Inflected Languages**: Languages like German, Turkish, Finnish, and Russian form long compound words or attach multiple suffixes to word roots. Character n-grams naturally capture prefixes, suffixes, and morphological roots.
3. **Devanagari Disambiguation (Hindi vs. Marathi)**: Both languages share the Devanagari Unicode block (`\u0900-\u097F`). Character n-grams capture distinguishing morphemes (e.g. Hindi auxiliaries `है`, `था`, `रहा` vs. Marathi verbs `आहे`, `होता`, `काय`, `झाले`), allowing the model to achieve over 97% F1-score on both.
4. **Noise & Typo Resilience**: In conversational or social media text, misspelled words still retain most of their character sub-sequences, preventing the zero-count out-of-vocabulary penalty common in word-based models.

---

## Dataset

- **File**: `data/language_dataset.csv`
- **Schema**: `text,language`
- **Total Samples**: 1,500 balanced samples (100 curated authentic sentences per language).
- **Domains Covered**: Daily conversations, news headlines, literature, technical descriptions, questions, greetings, proverbs, and scientific discourse.
- **Source**: Curated multi-lingual corpus with native script preservation and ethical open-source distribution under the MIT license.

---

## Model Evaluation Results

Trained with a **stratified 80/20 train/test split** (1,200 training samples, 300 held-out test samples):

| Metric | Score |
| :--- | :--- |
| **Accuracy** | **99.00%** |
| **Macro Precision** | **99.02%** |
| **Macro Recall** | **99.00%** |
| **Macro F1-Score** | **99.00%** |
| **Weighted F1-Score** | **99.00%** |

### Per-Class Performance (Held-out Test Set)

```text
              precision    recall  f1-score   support

      Arabic     1.0000    1.0000    1.0000        20
     Chinese     1.0000    1.0000    1.0000        20
       Dutch     1.0000    1.0000    1.0000        20
     English     1.0000    1.0000    1.0000        20
      French     1.0000    1.0000    1.0000        20
      German     1.0000    1.0000    1.0000        20
       Hindi     1.0000    0.9500    0.9744        20
     Italian     1.0000    1.0000    1.0000        20
    Japanese     1.0000    1.0000    1.0000        20
      Korean     1.0000    1.0000    1.0000        20
     Marathi     0.9524    1.0000    0.9756        20
  Portuguese     0.9500    0.9500    0.9500        20
     Russian     1.0000    1.0000    1.0000        20
     Spanish     0.9500    0.9500    0.9500        20
     Turkish     1.0000    1.0000    1.0000        20

    accuracy                         0.9900       300
   macro avg     0.9902    0.9900    0.9900       300
weighted avg     0.9902    0.9900    0.9900       300
```

---

## Project Structure

```text
language-detector/
│
├── app/
│   ├── __init__.py
│   └── main.py                # FastAPI REST API application
│
├── src/
│   ├── __init__.py            # Package initialization
│   ├── preprocessing.py       # Unicode normalization & script cleaning
│   ├── train.py               # Model training & evaluation pipeline
│   └── predict.py             # Inference engine & CLI runner
│
├── data/
│   ├── language_dataset.csv   # Balanced multi-language dataset
│   ├── create_dataset.py      # Base dataset generation script
│   ├── expand_dataset.py      # Expansion batch 1 script
│   └── expand_dataset_batch2.py# Expansion batch 2 script
│
├── models/
│   ├── language_detector.pkl  # Trained serialized scikit-learn pipeline
│   └── model_metadata.json    # Model evaluation metrics & metadata
│
├── frontend/
│   ├── index.html             # Standalone responsive UI
│   ├── style.css              # Dark modern aesthetic CSS
│   └── script.js              # Vanilla client interaction script
│
├── tests/
│   ├── __init__.py
│   ├── test_model.py          # Unit tests for ML pipeline & languages
│   └── test_api.py            # API integration tests for FastAPI
│
├── src/                       # React frontend for live dashboard
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
│
├── server.ts                  # Express full-stack proxy & Vite runner
├── requirements.txt           # Python dependencies
├── package.json               # Node.js dependencies & scripts
├── tsconfig.json              # TypeScript configuration
├── vite.config.ts             # Vite build configuration
├── .gitignore
├── LICENSE                    # MIT License
└── README.md
```

---

## Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/<your-username>/language-detector.git
cd language-detector
```

### 2. Set Up Python Virtual Environment

```bash
python3 -m venv venv

# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Training the Model

To train the model on `data/language_dataset.csv` and regenerate `models/language_detector.pkl`:

```bash
python -m src.train
```

The script will:
1. Load and validate `data/language_dataset.csv`.
2. Perform stratified 80/20 train/test splitting.
3. Fit character TF-IDF vectorizer and multinomial logistic regression.
4. Output the full classification report and evaluation metrics.
5. Save the trained pipeline to `models/language_detector.pkl` and metadata to `models/model_metadata.json`.

---

## Running Automated Tests

Run the complete test suite with `pytest`:

```bash
pytest -v tests/
```

Test coverage includes:
- Language detection tests for English, Hindi, Marathi, French, German, Spanish, Italian, Portuguese, Russian, Arabic, Chinese, Japanese, Korean, Dutch, and Turkish.
- Edge cases: empty text, whitespace-only, very short input (<2 characters).
- Script identification tests.
- FastAPI endpoint tests (`/`, `/health`, `/predict`, `/languages`, `/metrics`).

---

## Running the API & Frontend

### Option A: Run FastAPI Backend Directly

```bash
uvicorn app.main:app --reload --port 8000
```

- **Interactive API Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
- **Standalone Web App**: [http://localhost:8000/app](http://localhost:8000/app)

### Option B: Run Full-Stack React + Node.js Server

```bash
npm install
npm run dev
```

Opens the full React NLP Dashboard at [http://localhost:3000](http://localhost:3000).

---

## API Documentation

### 1. `POST /predict`

Detects the language of the provided text.

**Request:**

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "Bonjour, comment allez-vous aujourd hui?"}'
```

**Response:**

```json
{
  "language": "French",
  "confidence": 0.824,
  "percentage": "82.4%",
  "flag": "🇫🇷",
  "code": "fr",
  "native": "Français",
  "script": "Latin",
  "family": "Indo-European / Romance",
  "detected_script": "Latin",
  "character_count": 40,
  "cleaned_length": 39,
  "prediction": {
    "language": "French",
    "confidence": 0.824,
    "percentage": "82.4%",
    "flag": "🇫🇷",
    "code": "fr",
    "native": "Français",
    "script": "Latin"
  },
  "alternatives": [
    {
      "language": "French",
      "confidence": 0.824,
      "percentage": "82.4%",
      "code": "fr",
      "flag": "🇫🇷",
      "native": "Français",
      "script": "Latin"
    },
    {
      "language": "English",
      "confidence": 0.038,
      "percentage": "3.8%",
      "code": "en",
      "flag": "🇬🇧",
      "native": "English",
      "script": "Latin"
    },
    {
      "language": "Spanish",
      "confidence": 0.027,
      "percentage": "2.7%",
      "code": "es",
      "flag": "🇪🇸",
      "native": "Español",
      "script": "Latin"
    }
  ]
}
```

### 2. `GET /health`

**Response:**

```json
{
  "status": "healthy",
  "model_loaded": true,
  "supported_languages_count": 15,
  "version": "1.0.0"
}
```

### 3. `GET /languages`

Returns all 15 supported languages, flags, ISO codes, and writing systems.

---

## Limitations

1. **Very Short Text**: Inputs with fewer than 2–3 characters (such as single words or abbreviations like "hi", "in") may have ambiguous n-gram distributions shared across multiple Germanic or Romance languages.
2. **Code-Mixed Text**: Sentences with heavy code-mixing (such as Hinglish: *"Mujhe meeting attend karni hai"*) contain Hindi vocabulary written in Latin script, which traditional mono-lingual models will classify by dominant script or character distribution.
3. **Confidence as Probability Estimate**: Confidence values represent model posterior probabilities via softmax over the trained class distribution, not an absolute statistical proof.

---

## Future Improvements

- [ ] Incorporate fine-tuned multilingual transformer models (e.g. XLM-RoBERTa, mBERT) for sentence embeddings.
- [ ] Add support for code-mixed text detection (Hinglish, Spanglish).
- [ ] Add batch prediction endpoint for processing CSV / JSON lines files.
- [ ] Multi-label classification for multilingual documents containing multiple languages.
- [ ] Containerize application with Docker and Docker Compose.

---

## Git Commands to Publish to GitHub

```bash
git init
git add .
git commit -m "feat: complete language detection system with NLP, ML pipeline, FastAPI & modern dashboard"
git branch -M main
git remote add origin https://github.com/<your-username>/language-detector.git
git push -u origin main
```

---

## License

This project is licensed under the [MIT License](LICENSE).

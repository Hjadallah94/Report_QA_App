# Report QA App

> A production-ready NLP application for automated document quality assurance, deployed to real users.

## Overview

This is a **full-stack Streamlit application** that provides automated quality assurance for business reports and documents. The application has been **deployed to production** and used by real users to analyze and improve document quality at scale.

### Key Features

- **Multi-format Support**: Upload and analyze DOCX or PDF documents (up to ~40 pages / ~20 MB)
- **Comprehensive NLP Checks**: 
  - Grammar and spelling validation (English & Arabic support)
  - Subjectivity and bias detection using ML models
  - Passive voice identification
  - Repetition and vagueness analysis
  - Required section validation
  - Optional LLM-powered deep analysis
- **Bilingual**: English and Arabic language support
- **Export & Reporting**: Download findings as CSV for further analysis
- **Production-Ready**: Deployed on Streamlit Cloud with environment-based configuration

## Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **NLP Processing**: spaCy, custom ML models (scikit-learn)
- **Document Parsing**: python-docx, pdfplumber
- **Optional AI**: OpenAI API integration for advanced analysis
- **Deployment**: Streamlit Cloud (production), containerizable architecture

## Quick Start

### Prerequisites
- Python **3.10+** ([download here](https://www.python.org/downloads/))
- On Windows, ensure "Add python.exe to PATH" is checked during installation

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>  # Replace with your actual GitHub repository URL
cd Report_qa_app
```

2. **Create a virtual environment**
```bash
python -m venv .venv
```

3. **Activate the virtual environment**
- Windows:
```bash
.venv\Scripts\activate
```Production Deployment

This application is deployed to **Streamlit Cloud** and accessible to production users.

### Deploy to Streamlit Cloud

1. **Push to GitHub**
```bash
git add .
git commit -m "Deploy to production"
git push origin main
```

2. **Configure Streamlit Cloud**
- Visit [Streamlit Cloud](https://share.streamlit.io)
- Create a new app pointing to your repository
- Set `app.py` as the entrypoint

3. **Environment Variables** (optional, for LLM features)

In Streamlit Cloud app settings, configure:
- `OPENAI_API_KEY` — Required for LLM-based checks
- `OPENAI_MODEL` — Optional (defaults to `gpt-3.5-turbo`)
- `OPENAI_TEMPERATURE` — Optional (defaults to `0.0`)
- `OPENAI_MAX_TOKENS` — Optional (defaults to `512`)

### Local Development with Secrets

Create `.streamlit/secrets.toml` (git-ignored) for local testing:

```toml
# .streamlit/secrets.toml (local only — do NOT commit)
[default]
OPENAI_API_KEY = "sk-..."
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_TEMPERATURE = "0.0"
OPENAI_MAX_TOKENS = "512"
```

Or set environment variables in your terminal:

```bash
# Windows PowerShell
$env:OPENAI_API_KEY="sk-..."
streamlit run app.py

# macOS/Linux
export OPENAI_API_KEY="sk-..."
streamlit run app.py
```

## Project Structure

```
Report_qa_app/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── config/                         # Rule configurations
│   ├── rules_en.yml               # English rules
│   └── rules_ar.yml               # Arabic rules
├── parsers/                        # Document parsers
│   ├── docx_parser.py             # DOCX processing
│   └── pdf_parser.py              # PDF processing
├── rules_engine/                   # NLP rule engine
│   ├── checks.py                  # Core checks
│   ├── checks_spacy.py            # spaCy-based checks
│   ├── checks_subjectivity_ml.py  # ML-based subjectivity
│   ├── checks_llm.py              # Optional LLM checks
│   └── engine.py                  # Rules orchestration
├── models/                         # Trained ML models
│   └── subjectivity.joblib        # Subjectivity classifier
├── utils/                          # Utility functions
└── tests/                          # Unit tests

```

## Features in Detail

### 1. Grammar & Spelling
- English spelling via spaCy dictionaries
- Customizable ignore lists for domain-specific terms

### 2. Subjectivity & Bias Detection
- Machine learning classifier (scikit-learn)
- Trained on labeled dataset of subjective vs objective text
- Identifies opinion-based language

### 3. Passive Voice Detection
- Heuristic-based passive voice identification
- Configurable threshold for acceptable passive ratio

### 4. Repetition Analysis
- Detects overused words (excluding stopwords)
- Configurable per-1000-word threshold

### 5. Required Sections
- Validates presence of mandatory sections
- Customizable per language/domain

### 6. Vagueness Detection
- Identifies placeholder text (TBD, etc.)
- Flags ambiguous phrasing

### 7. Optional LLM Enhancement
- Deep semantic analysis via OpenAI API
- Context-aware suggestions
- Disabled by default (opt-in)

## Configuration

Edit `config/rules_en.yml` or `config/rules_ar.yml` to customize:
- Check enablement/disablement
- Severity thresholds
- Ignore lists
- Language-specific rules

Example:
```yaml
spelling:
  enabled: true
  language: en_GB
  ignore:
    - UAE
    - API
```

## Testing

Run unit tests:
```bash
pytest tests/
```

Run specific test file:
```bash
pytest tests/test_subjectivity_ml.py
```

## Notes & Limitations

- **Spelling**: English-only (Arabic spelling disabled)
- **Passive tone**: Heuristic-based estimation (can be refined)
- **File size**: Optimized for documents up to ~40 pages / 20 MB
- **Privacy**: Files processed in-memory only, not persisted
- **LLM features**: Optional, requires API key

## License

This project is available for portfolio and demonstration purposes.

## Contact

For questions about this production application, please reach out via GitHub issue
3. Local testing (PowerShell): to run the app locally and supply a key for dev use, set env vars in your session first:

```powershell
- Filter, review results, and click **Download CSV** to export findings.

## Notes
- **Spelling** check is **English-only** (Arabic spelling disabled).
streamlit run app.py
```

4. Alternative local secret file: for local development you may add a `.streamlit/secrets.toml` (do NOT commit secrets) with the following structure:

```toml
# .streamlit/secrets.toml (local only — do NOT commit)
[default]
OPENAI_API_KEY = "sk-..."
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_TEMPERATURE = "0.0"
OPENAI_MAX_TOKENS = "512"
```

5. Example `.streamlit/streamlit_app.toml` (app config): see the companion example file `.streamlit/streamlit_app.toml` in this repo for recommended runtime settings (title, headless behaviour). Note that environment variables are configured either via Streamlit Cloud app settings or via `.streamlit/secrets.toml` for local testing.
- **Passive tone** is estimated with a simple heuristic. You can refine rules later.
- Uploaded files are held only in memory and discarded after analysis.
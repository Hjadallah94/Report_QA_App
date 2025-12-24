# CEERISK Report QA App (MVP)

This is a minimal **Streamlit** app that lets a user upload a **DOCX or PDF** (up to ~40 pages / ~20 MB),
runs rule-based checks (grammar basics, spelling, subjective/bias language, passive tone cues, required sections, repetition),
and shows/export issues to **CSV**.

## 0) Install Python
- Windows/macOS: Install Python **3.10+** from https://www.python.org/downloads/
- During install on Windows, tick **"Add python.exe to PATH"**.

## 1) Open a terminal in this folder
- Windows: Press Start, type **cmd**, press Enter, then `cd` to this folder.
- macOS: Open **Terminal** app, `cd` to this folder.

## 2) Create a virtual environment (recommended)
```
python -m venv .venv
```
Activate it:
- Windows:
```
.venv\Scripts\activate
```
- macOS/Linux:
```
source .venv/bin/activate
```

## 3) Install dependencies
```
pip install -r requirements.txt
```

## 4) Run the app

## 5) Use the app

## Deployment (Streamlit Cloud)

Below are quick instructions to deploy this app to Streamlit Cloud and how to supply required environment variables such as `OPENAI_API_KEY`.

1. Push your repo to GitHub (example PowerShell):

```powershell
git add .
git commit -m "Prepare app for deploy"
git push origin main
```

2. On Streamlit Cloud (https://share.streamlit.io) create a new app and point it at this repository and `app.py` as the entrypoint. In the app settings you can add environment variables and secrets.

- Recommended env vars to set in Streamlit Cloud app settings:
	- `OPENAI_API_KEY` — required if you enable LLM-based checks
	- `OPENAI_MODEL` — optional (defaults to `gpt-3.5-turbo`); change only if your account supports the model
	- `OPENAI_TEMPERATURE` — optional (defaults to `0.0`)
	- `OPENAI_MAX_TOKENS` — optional (defaults to `512`)

3. Local testing (PowerShell): to run the app locally and supply a key for dev use, set env vars in your session first:

```powershell
- Filter, review results, and click **Download CSV** to export findings.

## Notes
- **Spelling** check is **English-only** in this MVP (Arabic spelling disabled).
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
- **Passive tone** is estimated with a simple heuristic (for MVP). You can refine rules later.
- Uploaded files are held only in memory and discarded after analysis.
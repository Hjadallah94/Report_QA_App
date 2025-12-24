"""Lightweight LLM-based checks (optional, hosted API prototype).

This module provides a helper that asks a hosted LLM (OpenAI) to map
document text to the canonical required sections configured in rules.
It is optional: if `openai` is not installed or `OPENAI_API_KEY` is not
set, the functions return (available=False, error) and the app falls
back to rule-based checks.
"""

from typing import List, Dict, Tuple
import os
import json

OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
# Configurable model and parameters via env vars. Default model upgraded to 'gpt-5'.
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
try:
    OPENAI_TEMPERATURE = float(os.environ.get("OPENAI_TEMPERATURE", "0.0"))
except Exception:
    OPENAI_TEMPERATURE = 0.0
try:
    OPENAI_MAX_TOKENS = int(os.environ.get("OPENAI_MAX_TOKENS", "512"))
except Exception:
    OPENAI_MAX_TOKENS = 512

try:
    import openai
except Exception:
    openai = None


def llm_available() -> Tuple[bool, str | None]:
    if openai is None:
        return False, "openai package not installed"
    if not OPENAI_KEY:
        return False, "OPENAI_API_KEY not set"
    return True, None


def _extract_headlines(text: str, meta: Dict | None = None) -> str:
    """Extract likely heading lines from document structure when available.

    Prefer using `meta["paragraphs"]` if provided by the parsers (DOCX/PDF).
    Falls back to a lightweight line-based heuristic on `text` otherwise.
    """
    # Use paragraphs from meta when available (more reliable for DOCX)
    if meta and isinstance(meta.get("paragraphs"), (list, tuple)) and meta.get("paragraphs"):
        paras = [p.strip() for p in meta.get("paragraphs") if p and p.strip()]
        candidates = []
        for p in paras:
            # Heuristic: headings are relatively short and capitalised/title-case
            if len(p) <= 120 and (p == p.title() or len(p.split()) <= 6):
                candidates.append(p)
        if candidates:
            return "\n".join(candidates[:50])

    # Fallback to previous line-based heuristic
    if not text:
        return ""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    candidates = []
    for l in lines:
        if len(l) <= 80 and (l == l.title() or len(l.split()) <= 5):
            candidates.append(l)
    if not candidates:
        candidates = lines[:10]
    return "\n".join(candidates)


def check_required_sections_llm(text: str, meta: Dict | None, cfg: Dict) -> List[Dict]:
    """Ask an LLM to detect which canonical sections are present, then
    return issues for any required sections missing according to the LLM.

    Returns an empty list if the LLM integration is unavailable.
    """
    issues: List[Dict] = []
    available, err = llm_available()
    if not available:
        return issues

    required = cfg.get("required_sections", [])
    if not required:
        return issues

    # Build a prompt that asks the model to map the document to canonical sections.
    headlines = _extract_headlines(text, meta)
    prompt = (
        "You are a concise assistant. Given the document text (or its headings), "
        "and a list of canonical sections, return a JSON array containing the canonical "
        "section names that are present in the document. Only return valid JSON."
    )

    system = "You are a small utility that maps document content to canonical section names."
    user = (
        f"CANONICAL SECTIONS:\n{json.dumps(required, ensure_ascii=False, indent=2)}\n\n"
        f"DOCUMENT HEADLINES / SNIPPET:\n{headlines}\n\n"
        "Return a JSON array, e.g. [\"Executive Summary\", \"Findings\"]."
    )

    try:
        openai.api_key = OPENAI_KEY
        # Use configurable model + params
        resp = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=OPENAI_MAX_TOKENS,
            temperature=OPENAI_TEMPERATURE,
        )
        text_out = resp.choices[0].message.content.strip()
        # Attempt to parse JSON from the response
        try:
            found = json.loads(text_out)
            if not isinstance(found, list):
                found = []
        except Exception:
            # Try to extract JSON substring
            try:
                start = text_out.index("[")
                end = text_out.rindex("]") + 1
                found = json.loads(text_out[start:end])
            except Exception:
                found = []
    except Exception:
        return issues

    found_set = set([f.lower() for f in found if isinstance(f, str)])
    for sec in required:
        if sec.lower() not in found_set:
            issues.append({
                "rule_id": "required_sections_llm",
                "severity": "Major",
                "location": "Document",
                "snippet": f"Missing section (LLM check): {sec}",
                "suggestion": f"Add a clearly labeled '{sec}' section."
            })
    return issues

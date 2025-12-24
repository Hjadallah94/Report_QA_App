from typing import Dict, List
from collections import Counter
import re
import os

from utils.text_utils import split_sentences, get_snippet, find_occurrences

# A very small English stopword set for repetition check (extend as needed)
STOPWORDS = set(["the", "and", "or", "a", "an", "in", "on", "for", "to", "of", "with", "by", "is", "are", "was", "were", "it", "as", "at", "be", "that", "this", "these", "those", "from", "we", "our", "you", "your", "their", "they", "he", "she", "i", "my", "me", "us"])

def _issue(rule_id: str, severity: str, location: str, snippet: str, suggestion: str) -> Dict:
    return {
        "rule_id": rule_id,
        "severity": severity,
        "location": location,
        "snippet": snippet,
        "suggestion": suggestion,
    }

def check_required_sections(text: str, cfg: Dict) -> List[Dict]:
    issues = []
    sections = cfg.get("required_sections", [])
    for sec in sections:
        if re.search(rf"\b{re.escape(sec)}\b", text, flags=re.IGNORECASE) is None:
            issues.append(_issue(
                "required_sections",
                "Major",
                "Document",
                f"Missing section: {sec}",
                f"Add a clearly labeled '{sec}' section."
            ))
    return issues

def check_forbidden_phrases(text: str, cfg: Dict) -> List[Dict]:
    issues = []
    phrases = cfg.get("forbidden_phrases", [])
    for ph in phrases:
        for m in re.finditer(re.escape(ph), text, flags=re.IGNORECASE):
            issues.append(_issue(
                "forbidden_phrases",
                "Minor",
                f"Chars {m.start()}–{m.end()}",
                text[max(0, m.start()-70): m.end()+70].replace("\n", " ")[:140],
                f"Remove or rephrase '{ph}' to maintain objective tone."
            ))
    return issues

def check_subjective_language(text: str, cfg: Dict) -> List[Dict]:
    issues = []
    words = cfg.get("subjective_adjectives", [])
    for w in words:
        for m in re.finditer(rf"\b{re.escape(w)}\b", text, flags=re.IGNORECASE):
            issues.append(_issue(
                "subjective_language",
                "Minor",
                f"Chars {m.start()}–{m.end()}",
                text[max(0, m.start()-70): m.end()+70].replace("\n", " ")[:140],
                f"Replace subjective term '{w}' with evidence-based description (cite data)."
            ))
    return issues

def check_bias_phrases(text: str, cfg: Dict) -> List[Dict]:
    issues = []
    words = cfg.get("bias_phrases", [])
    for w in words:
        for m in re.finditer(rf"\b{re.escape(w)}\b", text, flags=re.IGNORECASE):
            issues.append(_issue(
                "bias_language",
                "Minor",
                f"Chars {m.start()}–{m.end()}",
                text[max(0, m.start()-70): m.end()+70].replace("\n", " ")[:140],
                f"Avoid absolute '{w}'. Use measured language (e.g., 'often', 'rarely')."
            ))
    return issues

def check_first_person(text: str, cfg: Dict) -> List[Dict]:
    issues = []
    if not cfg.get("disallow_first_person_pronouns", False):
        return issues
    pronouns = cfg.get("first_person_pronouns", [])
    for p in pronouns:
        for m in re.finditer(rf"\b{re.escape(p)}\b", text, flags=re.IGNORECASE):
            issues.append(_issue(
                "first_person",
                "Major",
                f"Chars {m.start()}–{m.end()}",
                text[max(0, m.start()-70): m.end()+70].replace("\n", " ")[:140],
                "Use impersonal or passive constructions; avoid first-person references."
            ))
    return issues

def check_repetition(text: str, cfg: Dict) -> List[Dict]:
    issues = []
    if not cfg.get("repetition", {}).get("enabled", False):
        return issues
    max_per_1000 = int(cfg["repetition"].get("max_per_1000", 25))
    ignore = set([w.lower() for w in cfg["repetition"].get("ignore", [])])

    tokens = re.findall(r"[A-Za-z']+", text.lower())
    total = max(1, len(tokens))
    c = Counter([t for t in tokens if t not in STOPWORDS and t not in ignore and len(t) > 2])

    for w, cnt in c.most_common(50):
        per_1000 = cnt * 1000.0 / total
        if per_1000 > max_per_1000:
            idx = text.lower().find(w)
            issues.append(_issue(
                "repetition",
                "Minor",
                f"First occurrence ~ char {idx}" if idx >= 0 else "Document",
                text[max(0, idx-70): idx+70].replace("\n", " ")[:140] if idx >= 0 else "",
                f"'{w}' repeated {cnt} times (~{per_1000:.1f}/1000 words). Consider synonyms or rephrasing."
            ))
    return issues

# Spelling checks removed — spellchecking was previously implemented with
# `pyspellchecker`. Those checks have been deleted per project simplification.

def check_passive_voice_ratio(text: str, cfg: Dict) -> List[Dict]:
    issues = []
    pv_cfg = cfg.get("passive_voice_required", {})
    if not pv_cfg.get("enabled", False):
        return issues
    min_ratio = float(pv_cfg.get("min_ratio", 0.15))
    sents = split_sentences(text)
    if not sents:
        return issues

    # naive passive cue: "was|were|is|are|been|being|be" + past participle + optional "by"
    # this is a very rough heuristic for MVP
    passive_re = re.compile(r"\b(?:was|were|is|are|been|being|be)\s+\w+(ed|en)\b(?:\s+by\b)?", re.IGNORECASE)
    passive_count = sum(1 for s in sents if passive_re.search(s) is not None)
    ratio = passive_count / max(1, len(sents))
    if ratio < min_ratio:
        issues.append(_issue(
            "passive_voice_ratio",
            "Minor",
            "Document",
            f"Passive-like constructions in ~{ratio*100:.0f}% of sentences (min required ~{int(min_ratio*100)}%).",
            "Use more impersonal/passive constructions for consistency (e.g., 'was conducted', 'were observed')."
        ))
    return issues

def check_placeholders_and_vague_phrases(text: str, cfg: Dict) -> List[Dict]:
    """
    Flags placeholder tokens (TBD, to be confirmed, N/A, not sure) and vague phrasing
    that the manager's review often highlighted as issues requiring concrete details.
    """
    issues: List[Dict] = []
    vcfg = cfg.get("vagueness_checks", {})
    if not vcfg.get("enabled", False):
        return issues

    placeholders = [p.lower() for p in vcfg.get("placeholders", [])]
    vague_phrases = [p.lower() for p in vcfg.get("vague_phrases", [])]

    lower_text = text.lower() if text else ""

    # placeholders
    for ph in placeholders:
        for (s, e) in find_occurrences(lower_text, ph):
            issues.append({
                "rule_id": "placeholder_token",
                "severity": "Major" if ph in {"tbd", "to be confirmed"} else "Minor",
                "location": f"Chars {s}–{e}",
                "snippet": get_snippet(text, s, e),
                "suggestion": f"Replace placeholder '{ph}' with a concrete value or remove before finalising the report."
            })

    # vague phrasing
    for vp in vague_phrases:
        for (s, e) in find_occurrences(lower_text, vp):
            issues.append({
                "rule_id": "vague_phrase",
                "severity": "Minor",
                "location": f"Chars {s}–{e}",
                "snippet": get_snippet(text, s, e),
                "suggestion": "Replace vague wording with a specific, evidence-backed statement or provide a data/source."
            })

    return issues


def check_missing_image_captions(text: str, cfg: Dict, meta: Dict | None = None) -> List[Dict]:
    """
    Heuristic: when an image-term (photo/picture/figure) appears but there's no nearby
    caption indicator (caption/Figure/Fig), flag it as possibly missing a caption.
    """
    issues: List[Dict] = []
    vcfg = cfg.get("vagueness_checks", {})
    icfg = vcfg.get("image_checks", {}) if vcfg else {}
    if not icfg.get("enabled", False):
        return issues

    image_terms = icfg.get("image_terms", [])
    caption_indicators = [c.lower() for c in icfg.get("caption_indicators", [])]
    severity = icfg.get("severity_missing_caption", "Minor")

    # If parser-provided metadata about images is available, use it first
    if meta and isinstance(meta, dict):
        imgs = meta.get("images") or []
        for im in imgs:
            nearby = (im.get("nearby_text") or "").lower()
            below = (im.get("below_text") or "").lower()
            ocr = (im.get("ocr_text") or "").lower()

            # Combine nearby_text, below_text and OCR result for caption detection
            combined = " ".join([t for t in (nearby, below, ocr) if t])

            # Recognise explicit figure/caption patterns (e.g., "Figure 1:", "Fig. 2")
            fig_pattern = re.compile(r"\b(fig(?:ure)?\.?\s*\d+)[\.:]?", flags=re.IGNORECASE)

            # If combined contains a caption indicator or a figure number, consider image captioned
            has_caption_indicator = any(ci.lower() in combined for ci in caption_indicators)
            has_figure_number = bool(fig_pattern.search(combined))

            if (has_caption_indicator or has_figure_number):
                # image has visible caption-like text; skip flagging
                continue

            # If any image-term appears in combined text without a caption indicator, flag missing caption
            if combined and any(it.lower() in combined for it in image_terms):
                issues.append({
                    "rule_id": "missing_image_caption",
                    "severity": severity,
                    "location": f"Page {im.get('page', '?')}",
                    "snippet": (combined or "[no nearby text]")[:140],
                    "suggestion": "Add a caption or figure number and a brief description for the image so the reader understands what it shows."
                })
        # If we found any issues using metadata, return them (avoid double flagging)
        if issues:
            return issues

    # Fallback to sentence-based heuristic when no image metadata available
    sents = split_sentences(text)
    # Recognise explicit figure/caption patterns in sentences too
    fig_pattern = re.compile(r"\b(fig(?:ure)?\.?\s*\d+)[\.:]?", flags=re.IGNORECASE)
    for i, sent in enumerate(sents):
        lower = sent.lower()
        # If sentence contains a figure-number or a caption indicator, treat as captioned
        if fig_pattern.search(lower) or any(ci in lower for ci in caption_indicators):
            continue
        if any(it.lower() in lower for it in image_terms):
            # check previous sentence for a caption (e.g., "Figure 1: ..." on previous line)
            prev_has_caption = False
            if i > 0:
                prev = sents[i-1].lower()
                if fig_pattern.search(prev) or any(ci in prev for ci in caption_indicators):
                    prev_has_caption = True
            if prev_has_caption:
                continue
            # if no nearby caption indicator, flag
            idx = text.find(sent)
            issues.append({
                "rule_id": "missing_image_caption",
                "severity": severity,
                "location": f"Sentence",
                "snippet": sent[:140],
                "suggestion": "Add a caption or figure number and a brief description for the image so the reader understands what it shows."
            })

    return issues
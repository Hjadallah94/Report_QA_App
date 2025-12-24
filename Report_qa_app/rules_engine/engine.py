from typing import Dict, List
from rules_engine.checks import (
    check_required_sections,
    check_forbidden_phrases,
    check_subjective_language,
    check_bias_phrases,
    check_first_person,
    check_repetition,
    check_passive_voice_ratio,
    check_placeholders_and_vague_phrases,
    check_missing_image_captions,
)
from rules_engine.checks_llm import check_required_sections_llm, llm_available

def evaluate(text: str, meta: Dict, cfg: Dict) -> List[Dict]:
    """Run all checks and return a list of issue dicts.
    Issue fields: rule_id, severity, location, snippet, suggestion
    """
    issues = []
    # Order matters for display; adjust as needed
    # Prefer an LLM-based required-section detector when available (optional).
    try:
        llm_ok, _ = llm_available()
    except Exception:
        llm_ok = False
    # Allow runtime toggles from UI via cfg keys `_enabled_checks` (list)
    enabled = set([c.lower() for c in (cfg.get("_enabled_checks") or [])])

    # Required sections (LLM-assisted if available) - only if enabled
    if "required_sections" in enabled:
        if llm_ok:
            issues += check_required_sections_llm(text, meta, cfg)
        else:
            issues += check_required_sections(text, cfg)

    if "first_person" in enabled:
        issues += check_first_person(text, cfg)

    if "forbidden_phrases" in enabled:
        issues += check_forbidden_phrases(text, cfg)

    if "subjective_language" in enabled:
        issues += check_subjective_language(text, cfg)

    if "bias_language" in enabled:
        issues += check_bias_phrases(text, cfg)

    if "vagueness" in enabled:
        issues += check_placeholders_and_vague_phrases(text, cfg)

    if "repetition" in enabled:
        issues += check_repetition(text, cfg)

    if "passive_voice_ratio" in enabled:
        issues += check_passive_voice_ratio(text, cfg)

    if "missing_image_caption" in enabled:
        # Pass parser metadata (if any) to image caption check
        issues += check_missing_image_captions(text, cfg, meta=meta)

    # Apply verbosity threshold (0-100) if provided by UI in cfg['_verbosity'].
    # Higher verbosity -> fewer suggestions. Map severity to numeric score
    # so a user-set threshold can filter out lower-severity items.
    try:
        verbosity = int(cfg.get("_verbosity", 0))
    except Exception:
        verbosity = 0

    severity_score = {
        "Critical": 90,
        "Major": 60,
        "Minor": 30,
    }

    if verbosity and isinstance(verbosity, int) and verbosity > 0:
        filtered = [iss for iss in issues if severity_score.get(iss.get("severity"), 50) >= verbosity]
        return filtered

    return issues
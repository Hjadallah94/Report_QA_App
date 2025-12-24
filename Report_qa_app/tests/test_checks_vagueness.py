import pytest

from rules_engine.rules_loader import load_rules
from rules_engine.checks import (
    check_placeholders_and_vague_phrases,
    check_missing_image_captions,
)


def test_placeholders_detected():
    cfg = load_rules("config/rules_en.yml")
    text = "The address is TBD. It is not clear."
    issues = check_placeholders_and_vague_phrases(text, cfg)
    assert any(i['rule_id'] == 'placeholder_token' for i in issues)


def test_vague_phrase_detected():
    cfg = load_rules("config/rules_en.yml")
    text = "It seems the results are conclusive."
    issues = check_placeholders_and_vague_phrases(text, cfg)
    assert any(i['rule_id'] == 'vague_phrase' for i in issues)


def test_missing_image_caption_flagged():
    cfg = load_rules("config/rules_en.yml")
    text = "The following picture shows the tank. The tank is damaged."
    issues = check_missing_image_captions(text, cfg)
    assert any(i['rule_id'] == 'missing_image_caption' for i in issues)


def test_image_with_caption_not_flagged():
    cfg = load_rules("config/rules_en.yml")
    text = "Figure 1: Layout of the plant. The image shows the boiler."
    issues = check_missing_image_captions(text, cfg)
    assert not any(i['rule_id'] == 'missing_image_caption' for i in issues)

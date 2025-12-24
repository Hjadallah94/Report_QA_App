"""
spaCy-based checks removed.

This module previously provided grammar-aware checks using spaCy
but has been neutralized per the user's request. The helpers below
are no-ops for backward compatibility.
"""

def spacy_available():
    return (False, "spaCy checks removed")


def check_passive_spacy(text: str):
    return []

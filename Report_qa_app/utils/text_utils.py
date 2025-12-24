import re
import regex
from typing import List, Tuple

SENTENCE_SPLIT_RE = regex.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")

def split_sentences(text: str) -> List[str]:
    if not text:
        return []
    parts = SENTENCE_SPLIT_RE.split(text.strip())
    return [p.strip() for p in parts if p.strip()]

def split_paragraphs(text: str) -> List[str]:
    # Split on double newlines or line breaks
    paras = [p.strip() for p in re.split(r"\n{2,}|\r\n{2,}", text) if p.strip()]
    if not paras:
        # fallback: split by single newline
        paras = [p.strip() for p in text.splitlines() if p.strip()]
    return paras

def find_occurrences(text: str, phrase: str) -> List[Tuple[int, int]]:
    # Returns list of (start, end) indices for case-insensitive matches
    out = []
    for m in regex.finditer(regex.escape(phrase), text, regex.IGNORECASE):
        out.append((m.start(), m.end()))
    return out

def get_snippet(text: str, start: int, end: int, max_len: int = 140) -> str:
    # Provide a short snippet around the match
    left = max(0, start - max_len // 2)
    right = min(len(text), end + max_len // 2)
    snippet = text[left:right].replace("\n", " ")
    return snippet[:max_len] + ("…" if len(snippet) > max_len else "")
"""Bilingual search helpers for Sri Lankan O/L (Tamil + English)."""

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher


# Bidirectional topic synonyms (Tamil ↔ English) for smart search.
_SYNONYM_GROUPS: list[set[str]] = [
    {"வரலாறு", "history", "hist"},
    {"புவியியல்", "geography", "geo"},
    {"விஞ்ஞானம்", "அறிவியல்", "science", "sci"},
    {"கணிதம்", "mathematics", "maths", "math"},
    {"அனுராதபுரம்", "anuradhapura", "anuradhapura kingdom"},
    {"பொலன்னறுவை", "polonnaruwa"},
    {"காலநிலை", "climate", "weather", "climatic"},
    {"மழை", "rainfall", "rain"},
    {"மண்", "soil"},
    {"வரைபடம்", "map", "maps"},
    {"ஒளிச்சேர்க்கை", "photosynthesis"},
    {"சுவாசம்", "respiration"},
    {"அணு", "atom", "atomic"},
    {"மூலக்கூறு", "molecule"},
    {"விசை", "force"},
    {"ஆற்றல்", "energy"},
    {"மின்னோட்டம்", "current", "electricity"},
    {"ஒளி", "light", "optics"},
    {"இரசாயனம்", "chemistry", "chemical"},
    {"உயிரியல்", "biology"},
    {"இயற்பியல்", "physics"},
    {"இருபடிச் சமன்பாடு", "quadratic", "quadratic equation", "quadratic equations"},
    {"இயற்கணிதம்", "algebra"},
    {"வடிவியல்", "geometry"},
    {"முக்கோணம்", "triangle"},
    {"வட்டம்", "circle"},
    {"சமன்பாடு", "equation", "equations"},
    {"சூத்திரம்", "formula", "formulae", "formulas"},
    {"தேர்வு", "exam", "ol", "o/l"},
    {"திருத்தம்", "revision", "revise"},
    {"சுருக்கம்", "summary"},
    {"குடியேற்றம்", "colonization", "colonial"},
    {"சுதந்திரம்", "independence"},
    {"இலங்கை", "sri lanka", "srilanka", "ceylon"},
    {"ஆறு", "river", "rivers"},
    {"மலை", "mountain", "mountains", "highland"},
    {"கடல்", "ocean", "sea", "coast"},
    {"மக்கள் தொகை", "population"},
    {"விவசாயம்", "agriculture", "farming"},
]


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    text = unicodedata.normalize("NFKC", str(value)).strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def contains_tamil(text: str) -> bool:
    return bool(re.search(r"[\u0B80-\u0BFF]", text or ""))


def expand_query_terms(query: str) -> list[str]:
    """Expand a search query with bilingual synonyms and token variants."""
    q = normalize_text(query)
    if not q:
        return []

    terms: set[str] = {q}
    # Individual tokens (Latin + Tamil chunks)
    tokens = re.findall(r"[\u0B80-\u0BFFa-z0-9]+", q)
    terms.update(tokens)

    for group in _SYNONYM_GROUPS:
        normalized_group = {normalize_text(x) for x in group}
        if q in normalized_group or any(t in normalized_group for t in tokens):
            terms.update(normalized_group)
            continue
        # Fuzzy hit against synonym labels
        for label in normalized_group:
            if len(label) >= 4 and SequenceMatcher(None, q, label).ratio() >= 0.78:
                terms.update(normalized_group)
                break
            for token in tokens:
                if len(token) >= 4 and SequenceMatcher(None, token, label).ratio() >= 0.78:
                    terms.update(normalized_group)
                    break

    # Drop very short noise
    return [t for t in terms if len(t) >= 2]


def fuzzy_ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()


def text_matches(haystack: str | None, terms: list[str], fuzzy_threshold: float = 0.72) -> bool:
    """Return True if any expanded term matches haystack (substring or fuzzy)."""
    text = normalize_text(haystack)
    if not text or not terms:
        return False
    for term in terms:
        if term in text:
            return True
        # Fuzzy only for longer terms to avoid false positives
        if len(term) >= 5 and fuzzy_ratio(term, text) >= fuzzy_threshold:
            return True
        # Also fuzzy against individual words in haystack
        for word in re.findall(r"[\u0B80-\u0BFFa-z0-9]+", text):
            if len(term) >= 4 and len(word) >= 4 and fuzzy_ratio(term, word) >= fuzzy_threshold:
                return True
    return False

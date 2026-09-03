import re
from typing import Dict, List, Tuple

from .classifier import classify_expression
from .utils import clean_expression, sentence_context


NUMBER_PATTERN = r"(?:\\d{1,3}(?:,\\d{3})+|\\d+)(?:\\.\\d+)?"
CURRENCY_PREFIXES = r"(?:₹|Rs\.?|rs\.?|INR|USD|EUR|€|£|\\$)"


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def detect_numeric_candidates(text: str) -> List[Tuple[str, int, int]]:
    patterns = [
        re.compile(r"(?:₹|Rs\.?|rs\.?|INR|USD|EUR|€|£|\$)\s*(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:\s*(?:crore|lakh|million|billion|thousand))?", re.IGNORECASE),
        re.compile(r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\s*(?:%|GB|MB|KB|kg|g|mg|cm|mm|km|m|ml|L|Hz|GHz|MHz|inch|inches|°C|C)", re.IGNORECASE),
        re.compile(r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\s*(?:st|nd|rd|th)", re.IGNORECASE),
        re.compile(r"(?:\d+(?:\.\d+)?\s*/\s*\d+(?:\.\d+)?)", re.IGNORECASE),
        re.compile(r"(?:\d{1,2}\s+(?:jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|september|oct|october|nov|november|dec|december)\s+\d{4}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})", re.IGNORECASE),
        re.compile(r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\s*(?:million|billion|thousand|hundred|crore|lakh)?\s*(?:users|students|employees|people|items|units|countries|customers|participants|products|visitors|tickets|records|books|orders|files|pages|samples|residents)", re.IGNORECASE),
        re.compile(r"(?:approximately\s+\d+(?:\.\d+)?\s*(?:million|billion|thousand|hundred|crore|lakh)?\s*(?:users|students|employees|people|items|units|countries|customers|participants|products|visitors|tickets|records|books|orders|files|pages|samples|residents))", re.IGNORECASE),
        re.compile(r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\s*%", re.IGNORECASE),
        re.compile(r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?=\s*\b(?:users|students|employees|people|items|units|countries|customers|participants|products|visitors|tickets|records|books|orders|files|pages|samples|residents)\b)", re.IGNORECASE),
        re.compile(r"(?:\b(?:19|20)\d{2}\b)", re.IGNORECASE),
    ]

    matches = []
    for pattern in patterns:
        for match in pattern.finditer(text):
            value = match.group(0)
            cleaned = clean_expression(value)
            if cleaned and len(cleaned) > 0:
                matches.append((cleaned, match.start(), match.end()))

    return deduplicate_matches(merge_overlapping_matches(matches))


def deduplicate_matches(matches: List[Tuple[str, int, int]]) -> List[Tuple[str, int, int]]:
    unique = []
    seen = set()
    for value, start, end in matches:
        key = (value.lower(), start, end)
        if key in seen:
            continue
        seen.add(key)
        unique.append((value, start, end))
    return unique


def merge_overlapping_matches(matches: List[Tuple[str, int, int]]) -> List[Tuple[str, int, int]]:
    if not matches:
        return []
    matches = sorted(matches, key=lambda item: item[1])
    merged = [list(matches[0])]
    for value, start, end in matches[1:]:
        last_value, last_start, last_end = merged[-1]
        if start <= last_end:
            if len(value) > len(last_value):
                merged[-1] = [value, last_start, end]
            else:
                merged[-1][2] = max(last_end, end)
        else:
            merged.append([value, start, end])
    return [(value, start, end) for value, start, end in merged]


def analyze_text(text: str) -> Dict:
    normalized = normalize_text(text or "")
    if not normalized:
        return {
            "success": False,
            "error": "Input text is empty.",
            "statistics": {"total": 0, "quantity": 0, "percentage": 0, "currency": 0, "measurement": 0, "ranking": 0, "date": 0},
            "expressions": []
        }

    matches = detect_numeric_candidates(normalized)
    matches = merge_overlapping_matches(matches)

    results = []
    for expression, start, end in matches:
        category, confidence = classify_expression(normalized, expression, start, end)
        results.append({
            "expression": expression,
            "category": category,
            "start": start,
            "end": end,
            "context": sentence_context(normalized, start, end),
            "confidence": round(float(confidence), 2),
        })

    stats = {
        "total": len(results),
        "quantity": sum(1 for item in results if item["category"] == "Quantity"),
        "percentage": sum(1 for item in results if item["category"] == "Percentage"),
        "currency": sum(1 for item in results if item["category"] == "Currency"),
        "measurement": sum(1 for item in results if item["category"] == "Measurement"),
        "ranking": sum(1 for item in results if item["category"] == "Ranking"),
        "date": sum(1 for item in results if item["category"] == "Date"),
    }

    return {
        "success": True,
        "text": normalized,
        "statistics": stats,
        "expressions": results,
    }

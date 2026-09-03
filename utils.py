import re
from typing import List

CATEGORY_ORDER = ["Quantity", "Percentage", "Currency", "Measurement", "Ranking", "Date"]
STAT_KEYS = ["quantity", "percentage", "currency", "measurement", "ranking", "date"]


def clean_expression(raw_text: str) -> str:
    return raw_text.strip(" \t\r\n,.;:!?()[]{}\"'")


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def count_words(text: str) -> int:
    if not text or not text.strip():
        return 0
    return len(re.findall(r"\b\w+\b", text))


def count_characters(text: str) -> int:
    return len(text)


def sentence_context(text: str, start_index: int, end_index: int, snippet_length: int = 140) -> str:
    if not text:
        return ""

    window_start = max(0, start_index - snippet_length)
    window_end = min(len(text), end_index + snippet_length)
    snippet = text[window_start:window_end]

    sentence_start = text.rfind(".", 0, start_index)
    sentence_end = text.find(".", end_index)
    if sentence_start == -1:
        sentence_start = max(0, start_index - snippet_length)
    if sentence_end == -1:
        sentence_end = min(len(text), end_index + snippet_length)

    sentence = text[sentence_start:sentence_end]
    if sentence.strip():
        clean_sentence = normalize_whitespace(sentence)
        if len(clean_sentence) <= 220:
            return clean_sentence

    return normalize_whitespace(snippet)


def category_key(label: str) -> str:
    return label.lower()


def safe_list(value: List[str]) -> List[str]:
    return value if isinstance(value, list) else []

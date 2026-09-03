import re


MEASUREMENT_UNITS = (
    "GB", "MB", "KB", "kg", "g", "mg", "cm", "mm", "km", "m", "ml", "L", "Hz",
    "GHz", "MHz", "inch", "inches", "°C", "C"
)
QUANTITY_CONTEXT_WORDS = (
    "users", "students", "employees", "people", "items", "units", "countries",
    "customers", "participants", "products", "visitors", "tickets", "records",
    "books", "orders", "files", "pages", "samples", "residents"
)
DATE_MONTHS = (
    "jan", "january", "feb", "february", "mar", "march", "apr", "april", "may", "jun", "june",
    "jul", "july", "aug", "august", "sep", "september", "oct", "october", "nov", "november",
    "dec", "december"
)


def is_currency_expression(expression: str) -> bool:
    pattern = re.compile(
        r"(?i)(?:₹|Rs\.?|rs\.?|INR|USD|EUR|€|£|\$)\s*(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:\s*(?:crore|lakh|million|billion|thousand))?"
    )
    return bool(pattern.search(expression))


def is_percentage_expression(expression: str) -> bool:
    return bool(re.search(r"(?i)(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\s*%", expression))


def is_ranking_expression(expression: str) -> bool:
    if re.search(r"(?i)\b\d+(?:\.\d+)?(?:st|nd|rd|th)\b", expression):
        return True
    if re.search(r"(?i)\b\d+(?:\.\d+)?\s*/\s*\d+(?:\.\d+)?\b", expression):
        return True
    return bool(re.search(r"(?i)\b(?:1st|2nd|3rd|4th|5th|6th|7th|8th|9th|10th|11th|12th|13th|14th|15th|16th|17th|18th|19th|20th)\s+place\b", expression))


def is_measurement_expression(expression: str) -> bool:
    pattern = re.compile(
        r"(?i)\b(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\s*(?:GB|MB|KB|kg|g|mg|cm|mm|km|m|ml|L|Hz|GHz|MHz|inch|inches|°C|C)\b"
    )
    return bool(pattern.search(expression))


def is_quantity_expression(expression: str) -> bool:
    if re.search(r"(?i)\b(?:approximately|about|around)\s+(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\s*(?:million|billion|thousand|hundred|crore|lakh)?\s*(?:" + "|".join(QUANTITY_CONTEXT_WORDS) + r")\b", expression):
        return True
    if re.search(r"(?i)\b(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\s*(?:million|billion|thousand|hundred|crore|lakh)?\s*(?:" + "|".join(QUANTITY_CONTEXT_WORDS) + r")\b", expression):
        return True
    return False


def has_date_context(text: str, start: int, end: int) -> bool:
    window = text[max(0, start - 80): min(len(text), end + 80)].lower()
    context = re.sub(r"\s+", " ", window)
    has_month = any(month in context for month in DATE_MONTHS)
    has_numeric_date = bool(re.search(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}", context))
    has_date_marker = bool(re.search(r"\b(?:on|since|from|by|date|published|updated|launched|deadline|valid until)\b", context))
    return has_month or (has_date_marker and has_numeric_date)


def is_date_expression(expression: str) -> bool:
    month_pattern = r"(?:jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|september|oct|october|nov|november|dec|december)"
    if re.search(rf"(?i)\b\d{{1,2}}\s+{month_pattern}\s+\d{{4}}\b", expression):
        return True
    if re.search(rf"(?i)\b\d{{1,2}}\s+{month_pattern}\b", expression):
        return True
    if re.search(r"(?i)\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", expression):
        return True
    if re.search(r"(?i)\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b", expression):
        return True
    return False


def classify_expression(text: str, expression: str, start: int, end: int) -> tuple[str, float]:
    normalized = expression.strip()
    if not normalized:
        return "Quantity", 0.0

    if is_currency_expression(normalized):
        return "Currency", 0.99
    if is_percentage_expression(normalized):
        return "Percentage", 0.98
    if is_ranking_expression(normalized):
        return "Ranking", 0.97
    if is_measurement_expression(normalized):
        return "Measurement", 0.96
    if is_date_expression(normalized):
        return "Date", 0.96

    if re.fullmatch(r"(?i)(?:19|20)\d{2}", normalized):
        if has_date_context(text, start, end):
            return "Date", 0.82
        return "Quantity", 0.68

    if is_quantity_expression(normalized):
        return "Quantity", 0.88

    if re.fullmatch(r"(?i)\d+(?:\.\d+)?", normalized):
        if has_date_context(text, start, end):
            return "Date", 0.72
        return "Quantity", 0.74

    return "Quantity", 0.65

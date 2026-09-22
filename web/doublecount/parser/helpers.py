import re
import unicodedata

from openpyxl.cell.cell import MergedCell


def extract_year(year_str: str, current_year: int):
    try:
        match = re.search("([0-9]{4})", str(year_str))
        year = match.group(0)
        return int(year)
    except Exception:
        return current_year


def intOrZero(value):
    try:
        return int(value)
    except Exception:
        return 0


def extract_country_code(country_str: str) -> str | None:
    if country_str:
        return (country_str or "").split(" - ")[0].strip()
    else:
        return None


def to_upper_snake_case(value: str) -> str:
    value = value.strip()
    value = value.translate(str.maketrans({"œ": "oe", "Œ": "OE", "æ": "ae", "Æ": "AE"}))
    value = unicodedata.normalize("NFKD", value)
    value = "".join(character for character in value if not unicodedata.combining(character))
    value = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", value)
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    value = re.sub(r"[^A-Za-z0-9]+", "_", value)
    return value.strip("_").upper()


def is_subtotal_row(row, start: int, end: int) -> bool:
    cells = row[start:end]
    return bool(cells) and cells[0].value is not None and all(isinstance(cell, MergedCell) for cell in cells[1:])

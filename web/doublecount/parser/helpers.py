import re


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

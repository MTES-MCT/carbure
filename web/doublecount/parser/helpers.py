import re


def extract_year(year_str: str, current_year: int):
    try:
        match = re.search("([0-9]{4})", str(year_str))
        year = match.group(0)
        return int(year)
    except:
        return current_year

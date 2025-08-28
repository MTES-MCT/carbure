from datetime import date


def get_declaration_period(year=None):
    """
    Determines the current declaration interval based on the current date.

    The declaration period extends from April 1st to March 31st of the following year.
    The year to declare depends on the current month:
    - If the current month is January-March: declare for the previous year
    - If the current month is April-December: declare for the current year

    Args:
        year: The year to check against the current declaration period

    Returns:
        bool: True if the given year matches the current declaration year, False otherwise
    """

    year = int(year) if year is not None else None
    current_date = date.today()

    current_year = current_date.year
    current_month = current_date.month

    declaration_year = current_year - 1 if current_month < 4 else current_year

    return {
        "start_date": date(declaration_year, 4, 1),
        "end_date": date(declaration_year + 1, 3, 31),
        "declaration_year": declaration_year,
        "is_valid": declaration_year == year,
    }

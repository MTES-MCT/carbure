from datetime import date


def get_declaration_period():
    """
    Determines the current declaration interval based on the current date.

    The declaration period extends from April 1st to March 31st of the following year.
    The year to declare depends on the current month:
    - If the current month is January-March: declare for the previous year
    - If the current month is April-December: declare for the current year

    Returns:
        int: The year corresponding to the current declaration period.
    """

    current_date = date.today()
    current_year = current_date.year
    current_month = current_date.month

    declaration_year = current_year - 1 if current_month < 4 else current_year

    return declaration_year

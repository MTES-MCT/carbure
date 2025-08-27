from datetime import date
from functools import wraps

from rest_framework.permissions import BasePermission
from web.core.common import ErrorResponse


def get_declaration_interval(year):
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
    if year is None:
        return False

    year = int(year)
    current_date = date.today()

    current_year = current_date.year
    current_month = current_date.month

    declaration_year = current_year - 1 if current_month < 4 else current_year

    return declaration_year == year


def check_declaration_period():
    def decorator(view_function):
        @wraps(view_function)
        def wrap(request, *args, **kwargs):
            year = request.request.query_params.get("year")
            is_valid = get_declaration_interval(year)

            if not is_valid:
                return ErrorResponse(status_code=400, error=["Year is not in declaration period"])
            return view_function(request, *args, **kwargs)

        return wrap

    return decorator


class CheckDeclarationPeriod(BasePermission):
    def has_permission(self, request, view):
        return get_declaration_interval(request.query_params.get("year"))

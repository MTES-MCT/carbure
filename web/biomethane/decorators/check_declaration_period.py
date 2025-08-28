from functools import wraps

from rest_framework.permissions import BasePermission
from web.core.common import ErrorResponse

from biomethane.utils.get_declaration_period import get_declaration_period


def check_declaration_period():
    def decorator(view_function):
        @wraps(view_function)
        def wrap(request, *args, **kwargs):
            year = request.request.query_params.get("year")
            declaration_interval = get_declaration_period(year)

            if not declaration_interval["is_valid"]:
                return ErrorResponse(status_code=400, error=["Year is not in declaration period"])
            return view_function(request, *args, **kwargs)

        return wrap

    return decorator


class CheckDeclarationPeriod(BasePermission):
    def has_permission(self, request, view):
        declaration_interval = get_declaration_period(request.query_params.get("year"))

        return declaration_interval["is_valid"]

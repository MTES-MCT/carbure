from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from tiruert.services.declaration_period import DeclarationPeriodService


@api_view(["GET"])
def declaration_period_is_open(request):
    """Check if the declaration period is open for the current year."""
    try:
        is_open = DeclarationPeriodService.is_declaration_period_open()
        year = DeclarationPeriodService.get_current_declaration_year()
        return Response(
            {
                "is_open": is_open,
                "year": year,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response(
            {"error": "DECLARATION_PERIOD_ERROR", "message": str(e)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

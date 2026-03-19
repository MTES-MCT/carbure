from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from tiruert.services.declaration_period import DeclarationPeriodService


@extend_schema(
    responses={
        200: {
            "type": "object",
            "properties": {
                "year": {"type": "integer"},
            },
        },
        503: {
            "type": "object",
            "properties": {
                "error": {"type": "string"},
                "message": {"type": "string"},
            },
        },
    },
)
@api_view(["GET"])
def curent_declaration_period(request):
    """Check if there is a current declaration period and return the year if there is one"""
    year = DeclarationPeriodService.get_current_declaration_year()

    if year is None:
        return Response(
            {"error": "DECLARATION_PERIOD_NOT_FOUND", "message": "No declaration period found for the current date."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return Response({"year": year}, status=status.HTTP_200_OK)

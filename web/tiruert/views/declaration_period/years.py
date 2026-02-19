from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from tiruert.models.declaration_period import TiruertDeclarationPeriod
from tiruert.services.declaration_period import DeclarationPeriodService


@extend_schema(
    responses={
        200: {
            "type": "object",
            "properties": {
                "years": {
                    "type": "array",
                    "items": {"type": "integer"},
                },
            },
        },
    },
)
@api_view(["GET"])
def declaration_period_years(request):
    """Return the list of past years until the current one"""
    current_period_year = DeclarationPeriodService.get_current_declaration_year()
    years = (
        TiruertDeclarationPeriod.objects.filter(year__lte=current_period_year)
        .order_by("year")
        .values_list("year", flat=True)
    )
    return Response({"years": list(years)}, status=status.HTTP_200_OK)

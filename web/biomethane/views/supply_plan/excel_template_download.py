from drf_spectacular.utils import OpenApiResponse, OpenApiTypes, extend_schema
from rest_framework.decorators import api_view

from biomethane.services.supply_plan_excel_template import create_supply_plan_template
from core.excel import ExcelResponse


@extend_schema(
    description="Download Supply Plan Excel Template",
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.BINARY,
            description="Fichier Excel généré",
        )
    },
)
@api_view(["GET"])
def download_template(request):
    file = create_supply_plan_template()
    return ExcelResponse(file)

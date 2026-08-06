from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, OpenApiTypes, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from biomethane.permissions import HasBiomethaneProducerRights
from biomethane.services.declaration_export import generate_annual_export
from core.excel import ExcelResponse


@extend_schema(
    parameters=[
        OpenApiParameter(name="entity_id", type=int, required=True, description="Authorised entity ID."),
        OpenApiParameter(name="year", type=int, required=True, description="Year of the declaration."),
    ],
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.BINARY,
            description="Fichier Excel généré",
        )
    },
)
@api_view(["GET"])
@permission_classes([HasBiomethaneProducerRights])
def export_annual_declaration(request):
    """Export all biomethane data for a producer and a given year as an Excel file."""
    year = request.query_params.get("year")
    if not year:
        return Response({"error": "year parameter is required"}, status=400)

    producer = request.entity
    if not producer:
        return Response({"error": "producer not found"}, status=404)

    excel_file = generate_annual_export(producer, int(year))
    return ExcelResponse(excel_file)

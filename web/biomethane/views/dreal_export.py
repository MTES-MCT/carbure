import os

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, OpenApiTypes, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from biomethane.permissions import CanDownloadDeclaration
from biomethane.services.dreal_export import generate_dreal_export
from core.excel import ExcelResponse


@extend_schema(
    parameters=[
        OpenApiParameter(name="entity_id", type=int, required=True, description="Authorised DREAL entity ID."),
        OpenApiParameter(name="year", type=int, required=True, description="Year of the declarations."),
    ],
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.BINARY,
            description="Fichier Excel généré",
        )
    },
)
@api_view(["GET"])
@permission_classes([CanDownloadDeclaration])
def export_dreal_annual_declaration(request):
    """Export validated biomethane declarations for a year as a flat Excel file, scoped by DREAL department access."""
    year = request.query_params.get("year")
    if not year:
        return Response({"error": "year parameter is required"}, status=400)

    entity = request.entity
    # Only export producers the requesting entity is allowed to access (DREAL/ADEME department scope)
    producer_ids = entity.get_allowed_entities().values_list("id", flat=True)
    excel_file = generate_dreal_export(producer_ids, int(year))
    try:
        return ExcelResponse(excel_file)
    finally:
        excel_file.close()
        try:
            os.unlink(excel_file.name)
        except OSError:
            pass

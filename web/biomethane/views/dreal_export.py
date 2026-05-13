import os

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, OpenApiTypes, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from biomethane.models import BiomethaneProductionUnit
from biomethane.permissions import HasDrealRights
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
@permission_classes([HasDrealRights])
def export_dreal_annual_declaration(request):
    """Export all biomethane declarations for a given year as a flat Excel file, filtered by DREAL department access."""
    year = request.query_params.get("year")
    if not year:
        return Response({"error": "year parameter is required"}, status=400)

    entity = request.entity
    accessible_dept_codes = entity.get_accessible_departments().values_list("code_dept", flat=True)
    production_units = BiomethaneProductionUnit.objects.filter(department__code_dept__in=accessible_dept_codes)

    excel_file = generate_dreal_export(production_units, int(year))
    try:
        return ExcelResponse(excel_file)
    finally:
        excel_file.close()
        try:
            os.unlink(excel_file.name)
        except OSError:
            pass

import time

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, OpenApiTypes, extend_schema
from rest_framework.decorators import action

from core.excel import ExcelResponse, export_to_excel


class ExcelExportActionMixin:
    @extend_schema(
        filters=True,
        parameters=[
            OpenApiParameter(
                name="selected_entity_id",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Entity whose operations are exported when acting as an administrator.",
                required=False,
            ),
        ],
        responses={
            (
                200,
                "application/vnd.ms-excel",
            ): OpenApiResponse(response=OpenApiTypes.BINARY, description="Excel file download"),
        },
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="export",
    )
    def export_operations_to_excel(self, request, *args, **kwargs):
        operations = self.filter_queryset(self.get_queryset())

        filename = f"tiruert_elec_operations_{request.entity}_{time.strftime('%Y-%m-%d_%H%M%S')}.xlsx"
        excel_file = export_to_excel(
            f"/tmp/{filename}",
            [
                {
                    "label": "Operations Export",
                    "rows": operations,
                    "columns": [
                        {"label": "Statut", "value": "status"},
                        {"label": "Date de création", "value": "created_at"},
                        {"label": "Type Opération", "value": "_operation"},
                        {"label": "Expéditeur", "value": "debited_entity.name"},
                        {"label": "Destinataire", "value": "credited_entity.name"},
                        {"label": "Quantité (MJ)", "value": "_quantity"},
                        {"label": "Tonnes CO2 eq. évitées", "value": "avoided_emissions"},
                    ],
                }
            ],
            column_width=20,
        )
        return ExcelResponse(excel_file)

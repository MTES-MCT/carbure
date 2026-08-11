import time

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, OpenApiTypes, extend_schema
from rest_framework.decorators import action

from core.excel import ExcelResponse, export_to_excel
from core.utils import truncate


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
                        {"label": "Date de création", "value": lambda o: o.created_at.strftime("%Y-%m-%d")},
                        {"label": "Type Opération", "value": "_operation"},
                        {"label": "Expéditeur", "value": "debited_entity.name"},
                        {"label": "Destinataire", "value": "credited_entity.name"},
                        {"label": "Quantité (MJ)", "value": lambda o: truncate(o.quantity, 0)},
                        {"label": "Tonnes CO2 eq. évitées", "value": lambda o: truncate(o.avoided_emissions)},
                    ],
                }
            ],
            column_width=20,
        )
        return ExcelResponse(excel_file)

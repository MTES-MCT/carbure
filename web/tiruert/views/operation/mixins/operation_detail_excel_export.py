import os
import tempfile
from datetime import datetime

from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework.decorators import action

from core.excel import ExcelResponse, export_to_excel
from tiruert.models import OperationDetail


class OperationDetailExcelExportActionMixin:
    @extend_schema(
        responses={(200, "application/vnd.ms-excel"): OpenApiTypes.BINARY},
        operation_id="export_tiruert_operation_details_excel",
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="export",
    )
    def export_operation_details_to_excel(self, request, *args, **kwargs):
        operation = self.get_object()
        details = (
            OperationDetail.objects.filter(operation=operation)
            .select_related("lot__biofuel", "lot__feedstock", "lot__country_of_origin")
            .only(
                "id",
                "operation_id",
                "lot_id",
                "volume",
                "emission_rate_per_mj",
                "lot__id",
                "lot__carbure_id",
                "lot__biofuel__code",
                "lot__feedstock__code",
                "lot__feedstock__category",
                "lot__country_of_origin__code_pays",
            )
            .order_by("id")
        )

        filename = f"tiruert_operation_{operation.id}_details_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path = os.path.join(tempfile.gettempdir(), filename)
        excel_file = export_to_excel(
            file_path,
            [
                {
                    "label": "Détails opération",
                    "rows": details,
                    "columns": [
                        {"label": "ID détail d'opération", "value": "id"},
                        {"label": "ID lot", "value": "lot.id"},
                        {"label": "ID CarbuRe du lot", "value": "lot.carbure_id"},
                        {"label": "Biocarburant", "value": "lot.biofuel.code"},
                        {"label": "Matière première", "value": "lot.feedstock.code"},
                        {"label": "Catégorie", "value": "lot.feedstock.category"},
                        {"label": "Pays d'origine", "value": "lot.country_of_origin.code_pays"},
                        {"label": "Période de durabilité", "value": lambda _: operation.durability_period},
                        {"label": "Volume utilisé (L)", "value": "volume"},
                        {"label": "Taux d'émission (gCO₂/MJ)", "value": "emission_rate_per_mj"},
                    ],
                }
            ],
            column_width=22,
            header_height=30,
        )
        return ExcelResponse(excel_file)

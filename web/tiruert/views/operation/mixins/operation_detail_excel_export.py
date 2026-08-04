import os
import tempfile
from datetime import datetime

from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework.decorators import action

from core.excel import ExcelResponse, export_to_excel
from core.utils import truncate
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
            OperationDetail._base_manager.filter(operation_id=operation.pk)
            .select_related("operation", "lot", "lot__biofuel", "lot__feedstock", "lot__country_of_origin")
            .order_by("lot__carbure_id")
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
                        {"label": "ID Carbure", "value": "lot.carbure_id"},
                        {"label": "Volume prélevé (L)", "value": lambda d: round(d.volume, 2)},
                        {"label": "Taux d'émission (gCO₂/MJ)", "value": "emission_rate_per_mj"},
                        {"label": "Émissions évitées (tCO₂)", "value": lambda d: truncate(d.avoided_emissions)},
                        {"label": "Biocarburant", "value": "lot.biofuel.name"},
                        {"label": "Matière première", "value": "lot.feedstock.name"},
                        {"label": "Catégorie", "value": "lot.feedstock.category"},
                    ],
                }
            ],
            column_width=22,
            header_height=30,
        )

        return ExcelResponse(excel_file)

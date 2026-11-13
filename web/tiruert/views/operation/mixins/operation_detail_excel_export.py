import os
import tempfile
from datetime import datetime

from drf_spectacular.utils import OpenApiResponse, OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.decorators import action

from core.excel import ExcelResponse, export_to_excel
from core.utils import truncate
from tiruert.models import OperationDetail


class OperationDetailExcelExportActionMixin:
    @extend_schema(
        responses={
            (status.HTTP_200_OK, "application/vnd.ms-excel"): OpenApiTypes.BINARY,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(response={"detail": "Not found."}, description="Operation not found"),
        },
        operation_id="export_tiruert_operation_details_excel",
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="export",
    )
    def export_operation_details_to_excel(self, request, *args, **kwargs):
        operation = self.get_object()
        is_ghg_event = operation.ghg_delta is not None
        has_corrected_emissions = operation.corrected_avoided_emissions is not None

        details = (
            OperationDetail._base_manager.filter(operation_id=operation.pk)
            .select_related("operation", "lot", "lot__biofuel", "lot__feedstock", "lot__country_of_origin")
            .order_by("lot__carbure_id")
        )

        columns = [
            {"label": "ID Carbure", "value": "lot.carbure_id"},
            {"label": "Volume prélevé (L)", "value": lambda d: None if is_ghg_event else round(d.volume, 2)},
            {
                "label": "Taux d'émission (gCO₂/MJ)",
                "value": "effective_emission_rate_per_mj"
                if has_corrected_emissions or is_ghg_event
                else "emission_rate_per_mj",
            },
            {
                "label": "Émissions évitées (tCO₂)",
                "value": lambda d: None
                if is_ghg_event
                else truncate(d.corrected_avoided_emissions if has_corrected_emissions else d.avoided_emissions),
            },
            {"label": "Biocarburant", "value": "lot.biofuel.name"},
            {"label": "Matière première", "value": "lot.feedstock.name"},
            {"label": "Catégorie", "value": "lot.feedstock.category"},
        ]
        if is_ghg_event:
            columns.append({"label": "Delta GES (gCO₂/MJ)", "value": "emission_rate_per_mj_delta"})

        filename = f"tiruert_operation_{operation.id}_details_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path = os.path.join(tempfile.gettempdir(), filename)

        excel_file = export_to_excel(
            file_path,
            [
                {
                    "label": "Détails opération",
                    "rows": details,
                    "columns": columns,
                }
            ],
            column_width=22,
            header_height=30,
        )

        return ExcelResponse(excel_file)

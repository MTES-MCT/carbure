import os
import tempfile
from datetime import datetime

from django.utils.text import slugify
from rest_framework.decorators import action

from core.excel import ExcelResponse, export_to_excel


class ExcelExportActionMixin:
    @action(
        detail=False,
        methods=["get"],
        url_path="export",
    )
    def export_supply_plan_to_excel(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        year = request.query_params.get("year")
        name = "qualicharge_certificates"
        filename = f"{name}_{year}_{slugify(request.entity.name)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path = os.path.join(tempfile.gettempdir(), filename)

        excel_file = export_to_excel(
            file_path,
            [
                {
                    "label": "Qualicharge",
                    "rows": self.get_serializer(queryset, many=True).data,
                    "columns": [
                        {"label": "Statut", "value": "validated_by"},
                        {"label": "Unité d'exploitation", "value": "operating_unit"},
                        {"label": "Station ID", "value": "station_id"},
                        {"label": "Début de la mesure", "value": "date_from"},
                        {"label": "Fin de la mesure", "value": "date_to"},
                        {"label": "Energie (MWh)", "value": "energy_amount"},
                        {"label": "Energie renouvelable (MWh)", "value": "renewable_energy"},
                    ],
                }
            ],
            column_width=15,
        )
        try:
            return ExcelResponse(excel_file)
        finally:
            excel_file.close()
            try:
                os.unlink(file_path)
            except OSError:
                pass

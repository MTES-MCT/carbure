import tempfile
import time

from rest_framework.decorators import action

from core.excel import ExcelResponse, export_to_excel
from core.utils import truncate
from tiruert.models.operation import Operation


class ExcelExportActionMixin:
    @action(
        detail=False,
        methods=["get"],
        url_path="export",
    )
    def export_operations_to_excel(self, request, *args, **kwargs):
        operations = self.filter_queryset(self.get_queryset())

        filename = f"tiruert_operations_{request.entity}_{time.strftime('%Y-%m-%d_%H%M%S')}.xlsx"
        file_path = f"{tempfile.gettempdir()}/{filename}"

        excel_file = export_to_excel(
            file_path,
            [
                {
                    "label": "Operations Export",
                    "rows": operations,
                    "columns": [
                        {"label": "Statut", "value": "status"},
                        {"label": "Filière", "value": "sector"},
                        {"label": "Biocarburant", "value": "biofuel.code"},
                        {"label": "Catégorie", "value": "customs_category"},
                        {"label": "Date de création", "value": lambda o: o.created_at.strftime("%Y-%m-%d")},
                        {"label": "Période de durabilité", "value": "durability_period"},
                        {"label": "Dépôt", "value": "_depot"},
                        {"label": "Type Opération", "value": "_type"},
                        {
                            "label": "Expéditeur",
                            "value": lambda o: o.debited_entity.name
                            if o.debited_entity and o._type != Operation.TENEUR
                            else "",
                        },
                        {"label": "Destinataire", "value": "credited_entity.name"},
                        {"label": "Volume (L)", "value": lambda o: truncate(o._volume)},
                        {"label": "Énergie (MJ)", "value": lambda o: truncate(o._energy, 0)},
                        {"label": "Tonnes CO2 eq. évitées", "value": lambda o: truncate(o.avoided_emissions)},
                    ],
                }
            ],
            column_width=20,
        )

        return ExcelResponse(excel_file)

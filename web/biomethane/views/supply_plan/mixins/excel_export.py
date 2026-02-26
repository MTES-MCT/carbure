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
        name = "biomethane_plan_approvisionnement"
        file = f"{name}_{year}_{slugify(request.entity.name)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        excel_file = export_to_excel(
            file,
            [
                {
                    "label": "Plan d'approvisionnement",
                    "rows": self.get_serializer(queryset, many=True).data,
                    "columns": [
                        {"label": "Intrant", "value": "feedstock"},
                        {"label": "Unité", "value": "material_unit"},
                        {"label": "Ratio de matière sèche (%)", "value": "dry_matter_ratio_percent"},
                        {"label": "Volume (t)", "value": "volume"},
                        {"label": "Département d'origine", "value": "origin_department"},
                        {"label": "Distance moyenne pondérée (km)", "value": "average_weighted_distance_km"},
                        {"label": "Distance maximale (km)", "value": "maximum_distance_km"},
                        {"label": "Pays d'origine", "value": "origin_country"},
                        {"label": "Type de CIVE", "value": "type_cive"},
                        {"label": "Précisez la culture", "value": "culture_details"},
                        {"label": "Type de collecte", "value": "collection_type"},
                        {"label": "Année", "value": "year"},
                    ],
                }
            ],
            column_width=15,
        )

        return ExcelResponse(excel_file)

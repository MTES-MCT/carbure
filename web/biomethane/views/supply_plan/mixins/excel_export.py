import os
import tempfile
from datetime import datetime

from django.utils.text import slugify
from rest_framework.decorators import action

from biomethane.permissions import HasDrealRights
from biomethane.services.supply_input_export import generate_supply_input_export
from core.excel import ExcelResponse


class ExcelExportActionMixin:
    @action(
        detail=False,
        methods=["get"],
        url_path="export",
    )
    def export_supply_plan_to_excel(self, request, *args, **kwargs):
        queryset = self.get_queryset().select_related(
            "supply_plan__producer__biomethane_production_unit__department",
            "feedstock__classification",
            "origin_country",
        )
        queryset = self.filter_queryset(queryset)

        year = request.query_params.get("year")
        name = "biomethane_plan_approvisionnement"
        filename = f"{name}_{year}_{slugify(request.entity.name)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path = os.path.join(tempfile.gettempdir(), filename)

        is_dreal = HasDrealRights().has_permission(request, self)
        rows = self.get_serializer(queryset, many=True).data
        excel_file = generate_supply_input_export(file_path, rows, dreal=is_dreal)

        try:
            return ExcelResponse(excel_file)
        finally:
            excel_file.close()
            try:
                os.unlink(file_path)
            except OSError:
                pass

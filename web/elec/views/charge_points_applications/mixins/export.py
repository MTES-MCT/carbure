from rest_framework.decorators import action

from core.excel import ExcelResponse
from elec.api.cpo.charge_points.charge_points import annotate_with_latest_meter_reading_date
from elec.services.export_charge_point_excel import export_charge_points_to_excel


class ExportActionMixin:
    @action(methods=["get"], detail=True)
    def export(self, request, id=None):
        application = self.get_object()
        charge_points = (
            application.elec_charge_points.filter(cpo=application.cpo, is_deleted=False)
            .order_by("station_id", "charge_point_id")
            .select_related("cpo")
        )
        charge_points = annotate_with_latest_meter_reading_date(charge_points)
        excel_file = export_charge_points_to_excel(charge_points, application.cpo)
        return ExcelResponse(excel_file)

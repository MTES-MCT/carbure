from django.views.decorators.http import require_GET
from core.common import SuccessResponse
from core.decorators import check_user_rights
from core.excel import ExcelResponse
from core.models import Entity
from elec.models import ElecChargePoint
from elec.serializers.elec_charge_point import ElecChargePointSerializer
from elec.services.export_charge_point_excel import export_charge_points_to_excel


@require_GET
@check_user_rights(entity_type=[Entity.CPO])
def get_charge_points(request, entity):
    charge_points = ElecChargePoint.objects.filter(cpo=entity)

    if "export" in request.GET:
        excel_file = export_charge_points_to_excel(charge_points, entity)
        return ExcelResponse(excel_file)

    serialized = ElecChargePointSerializer(charge_points, many=True).data
    return SuccessResponse(serialized)

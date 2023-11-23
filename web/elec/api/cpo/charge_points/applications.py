from django.db.models import Count, Sum
from django.views.decorators.http import require_GET
from core.common import SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity
from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.serializers.elec_charge_point_application import ElecChargePointApplicationSerializer


@require_GET
@check_user_rights(entity_type=[Entity.CPO])
def get_applications(request, entity):
    applications = ElecChargePointApplication.objects.filter(cpo=entity).annotate(
        station_count=Count("elec_charge_points__station_id", distinct=True),
        charging_point_count=Count("elec_charge_points__id"),
        power_total=Sum("elec_charge_points__meter_reading_energy"),
    )

    serialized = ElecChargePointApplicationSerializer(applications, many=True).data
    return SuccessResponse(serialized)

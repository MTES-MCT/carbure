from django.db.models import Count, Sum
from elec.models import ElecChargePointApplication


class ChargePointRepository:
    @staticmethod
    def get_annotated_applications(cpo):
        return ElecChargePointApplication.objects.filter(cpo=cpo).annotate(
            station_count=Count("elec_charge_points__station_id", distinct=True),
            charging_point_count=Count("elec_charge_points__id"),
            power_total=Sum("elec_charge_points__nominal_power"),
        )

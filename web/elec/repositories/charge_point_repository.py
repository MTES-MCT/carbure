from django.db.models import Count, Sum
from elec.models import ElecChargePointApplication
from elec.models.elec_charge_point import ElecChargePoint


class ChargePointRepository:
    @staticmethod
    def get_annotated_applications(cpo):
        return ElecChargePointApplication.objects.filter(cpo=cpo).annotate(
            station_count=Count("elec_charge_points__station_id", distinct=True),
            charging_point_count=Count("elec_charge_points__id"),
            power_total=Sum("elec_charge_points__nominal_power"),
        )

    @staticmethod
    def get_registered_charge_points(cpo):
        return (
            ElecChargePoint.objects.select_related("application")
            .filter(cpo=cpo, application__status=ElecChargePointApplication.ACCEPTED)
            .order_by("charge_point_id")
        )

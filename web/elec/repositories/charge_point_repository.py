from django.db.models import Count, Sum
from elec.models import ElecChargePointApplication
from elec.models.elec_charge_point import ElecChargePoint


class ChargePointRepository:
    @staticmethod
    def get_annotated_applications():
        return ElecChargePointApplication.objects.all().annotate(
            station_count=Count("elec_charge_points__station_id", distinct=True),
            charge_point_count=Count("elec_charge_points__id"),
            power_total=Sum("elec_charge_points__nominal_power"),
        )

    @staticmethod
    def get_annotated_applications_by_cpo(cpo):
        return ChargePointRepository.get_annotated_applications().filter(cpo=cpo)

    @staticmethod
    def get_annotated_application_charge_points(cpo, application: ElecChargePointApplication):
        return (
            ElecChargePoint.objects.filter(cpo=cpo, application=application.id)
            .order_by("station_id", "charge_point_id")
            .select_related("cpo")
        )

    @staticmethod
    def get_registered_charge_points(cpo):
        return ElecChargePoint.objects.select_related("application").filter(cpo=cpo).order_by("charge_point_id")

    @staticmethod
    def get_charge_points_for_meter_readings(cpo):
        return ChargePointRepository.get_registered_charge_points(cpo).filter(is_article_2=False)

    @staticmethod
    def get_replaced_charge_points(cpo, new_charge_points: list[str]):
        return ChargePointRepository.get_registered_charge_points(cpo).filter(charge_point_id__in=new_charge_points)

from django.db.models import Count, Q, Sum

from elec.models import ElecChargePointApplication
from elec.models.elec_charge_point import ElecChargePoint


class ChargePointRepository:
    @staticmethod
    def get_annotated_applications():
        return ElecChargePointApplication.objects.all().annotate(
            station_count=Count(
                "elec_charge_points__station_id",
                filter=Q(elec_charge_points__is_deleted=False),
                distinct=True,
            ),
            charge_point_count=Count(
                "elec_charge_points__id",
                filter=Q(elec_charge_points__is_deleted=False),
            ),
            power_total=Sum(
                "elec_charge_points__nominal_power",
                filter=Q(elec_charge_points__is_deleted=False),
            ),
        )

    @staticmethod
    def get_annotated_applications_by_cpo(cpo):
        return ChargePointRepository.get_annotated_applications().filter(cpo=cpo)

    @staticmethod
    def get_annotated_application_charge_points(cpo, application: ElecChargePointApplication):
        return (
            ElecChargePoint.objects.filter(cpo=cpo, application=application.id, is_deleted=False)
            .order_by("station_id", "charge_point_id")
            .select_related("cpo")
        )

    @staticmethod
    def get_registered_charge_points(cpo):
        return (
            ElecChargePoint.objects.select_related("application")
            .filter(cpo=cpo, is_deleted=False, application__status=ElecChargePointApplication.ACCEPTED)
            .order_by("charge_point_id")
        )

    @staticmethod
    def get_charge_points_for_meter_readings(cpo):
        return (
            ElecChargePoint.objects.select_related("application")
            .filter(cpo=cpo, is_deleted=False, is_article_2=False)
            .order_by("charge_point_id")
        )

    @staticmethod
    def get_replaced_charge_points(cpo, new_charge_points: list[str]):
        return (
            ElecChargePoint.objects.select_related("application")
            .filter(cpo=cpo, is_deleted=False, charge_point_id__in=new_charge_points)
            .order_by("charge_point_id")
        )

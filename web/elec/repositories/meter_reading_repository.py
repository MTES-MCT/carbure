from django.db.models import Count, F, Q, Sum

from core.models import Entity
from elec.models import ElecMeterReadingApplication
from elec.models.elec_charge_point import ElecChargePoint
from elec.models.elec_meter_reading import ElecMeterReading
from transactions.models.year_config import YearConfig


class MeterReadingRepository:
    @staticmethod
    def get_annotated_applications():
        return ElecMeterReadingApplication.objects.all().annotate(
            charge_point_count=Count("elec_meter_readings__id"),
            energy_total=Sum("elec_meter_readings__renewable_energy"),
        )

    @staticmethod
    def get_annotated_applications_details():
        return MeterReadingRepository.get_annotated_applications().annotate(
            power_total=Sum(
                "elec_meter_readings__meter__charge_point__nominal_power",
                filter=Q(elec_meter_readings__meter__charge_point__is_deleted=False),
            ),
        )

    @staticmethod
    def get_annotated_applications_by_cpo(cpo):
        return MeterReadingRepository.get_annotated_applications().filter(cpo=cpo)

    @staticmethod
    def get_cpo_application_for_quarter(cpo, year: int, quarter: int):
        return MeterReadingRepository.get_annotated_applications().filter(cpo=cpo, quarter=quarter, year=year).first()

    @staticmethod
    def get_cpo_meter_readings(cpo: Entity):
        return ElecMeterReading.objects.filter(cpo=cpo).select_related("meter", "meter__charge_point")

    @staticmethod
    def get_previous_application(cpo: Entity, quarter=None, year=None):
        applications = ElecMeterReadingApplication.objects.filter(cpo=cpo, status=ElecMeterReadingApplication.ACCEPTED)
        if quarter and year:
            applications = applications.filter(Q(year__lt=year) | (Q(year=year) & Q(quarter__lt=quarter)))
        return applications.order_by("-year", "-quarter").first()

    @staticmethod
    def get_replaceable_applications(cpo: Entity):
        return ElecMeterReadingApplication.objects.filter(
            cpo=cpo, status__in=[ElecMeterReadingApplication.PENDING, ElecMeterReadingApplication.REJECTED]
        )

    @staticmethod
    def get_application_meter_readings(cpo: Entity, application: ElecMeterReadingApplication):
        return ElecMeterReading.objects.filter(
            cpo=cpo, application=application, meter__charge_point__is_deleted=False
        ).select_related("meter", "meter__charge_point")

    @staticmethod
    def get_application_meter_readings_summary(cpo: Entity, application: ElecMeterReadingApplication):
        return (
            MeterReadingRepository.get_application_meter_readings(cpo, application)
            .values("extracted_energy", "renewable_energy", "reading_date")
            .annotate(charge_point_id=F("meter__charge_point__charge_point_id"))
        )

    @staticmethod
    def get_application_charge_points(cpo: Entity, application: ElecMeterReadingApplication):
        charge_point_ids = ElecMeterReading.objects.filter(cpo=cpo, application=application).values_list(
            "meter__charge_point_id", flat=True
        )
        return ElecChargePoint.objects.filter(pk__in=charge_point_ids, is_deleted=False)

    @staticmethod
    def get_renewable_share(year: int):
        instance = YearConfig.objects.get(year=year)
        return instance.renewable_share / 100

    @staticmethod
    def get_entities_without_application(quarter, year):
        return Entity.objects.annotate(
            meter_readings_charge_points_count=Count(
                "elec_charge_points",
                filter=Q(elec_charge_points__is_article_2=False, elec_charge_points__is_deleted=False),
                distinct=True,
            ),
            app_count=Count(
                "elec_meter_reading_applications",
                filter=Q(elec_meter_reading_applications__quarter=quarter, elec_meter_reading_applications__year=year),
                distinct=True,
            ),
        ).filter(app_count=0, meter_readings_charge_points_count__gt=0, entity_type=Entity.CPO)

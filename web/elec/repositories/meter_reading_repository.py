from django.db.models import Count, Sum, F, Q
from core.models import Entity
from elec.models import ElecMeterReadingApplication
from elec.models.elec_meter_reading import ElecMeterReading
from transactions.models.year_config import YearConfig


class MeterReadingRepository:
    @staticmethod
    def get_annotated_applications(cpo: Entity):
        return ElecMeterReadingApplication.objects.filter(cpo=cpo).annotate(
            charge_point_count=Count("elec_meter_readings__id"),
            energy_total=Sum("elec_meter_readings__renewable_energy"),
        )

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
        return (
            ElecMeterReading.objects.filter(cpo=cpo, application=application)
            .values("extracted_energy", "renewable_energy", "reading_date")
            .annotate(charge_point_id=F("charge_point__charge_point_id"))
        )

    @staticmethod
    def get_renewable_share(year: int):
        instance = YearConfig.objects.get(year=year)
        return instance.renewable_share / 100

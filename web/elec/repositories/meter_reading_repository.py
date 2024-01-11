from django.db.models import Count, Sum, F
from core.models import Entity
from elec.models import ElecMeterReadingApplication
from elec.models.elec_meter_reading import ElecMeterReading


class MeterReadingRepository:
    @staticmethod
    def get_annotated_applications(cpo: Entity):
        return ElecMeterReadingApplication.objects.filter(cpo=cpo).annotate(
            charging_point_count=Count("elec_meter_readings__id"),
            energy_total=Sum("elec_meter_readings__extracted_energy"),
        )

    @staticmethod
    def get_previous_application(cpo: Entity, quarter=None, year=None):
        applications = ElecMeterReadingApplication.objects.filter(cpo=cpo, status=ElecMeterReadingApplication.ACCEPTED)
        if quarter and year:
            applications = applications.filter(quarter__lt=quarter, year__lte=year)
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
            .values("extracted_energy")
            .annotate(charge_point_id=F("charge_point__charge_point_id"))
        )

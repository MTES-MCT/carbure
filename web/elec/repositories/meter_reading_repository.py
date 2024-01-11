from django.db.models import Count, Sum
from elec.models import ElecMeterReadingApplication


class MeterReadingRepository:
    @staticmethod
    def get_annotated_applications(cpo):
        return ElecMeterReadingApplication.objects.filter(cpo=cpo).annotate(
            charging_point_count=Count("elec_meter_readings__id"),
            energy_total=Sum("elec_meter_readings__extracted_energy"),
        )

    @staticmethod
    def get_previous_application(cpo, quarter=None, year=None):
        applications = ElecMeterReadingApplication.objects.filter(cpo=cpo, status=ElecMeterReadingApplication.ACCEPTED)
        if quarter and year:
            applications = applications.filter(quarter__lt=quarter, year__lte=year)
        return applications.order_by("-year", "-quarter").first()

    @staticmethod
    def get_replaceable_applications(cpo):
        return ElecMeterReadingApplication.objects.filter(
            cpo=cpo, status__in=[ElecMeterReadingApplication.PENDING, ElecMeterReadingApplication.REJECTED]
        )

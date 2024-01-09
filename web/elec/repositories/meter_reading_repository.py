from django.db.models import Count, Sum
from elec.models import ElecMeterReadingApplication


class MeterReadingRepository:
    @staticmethod
    def get_annotated_applications(cpo):
        return ElecMeterReadingApplication.objects.filter(cpo=cpo).annotate(
            charging_point_count=Count("elec_meter_readings__id"),
            energy_total=Sum("elec_meter_readings__extracted_energy"),
        )

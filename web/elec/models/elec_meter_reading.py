from django.db import models
from django.db.models import F, OuterRef, Subquery
from django.db.models.functions import Coalesce

from core.models import Entity
from elec.models.elec_meter import ElecMeter
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication


class ExtendedMeterReadingManager(models.Manager):
    def get_queryset(self):
        readings = ElecMeterReading.objects.all()
        prev_readings = readings.filter(meter_id=OuterRef("meter_id"), pk__lt=OuterRef("pk")).order_by("-pk")[:1]
        prev_index = Subquery(prev_readings.values("extracted_energy"))
        prev_index_date = Subquery(prev_readings.values("reading_date"))

        return (
            super()
            .get_queryset()
            .select_related("meter", "meter__charge_point")
            .annotate(reading_id=F("id"), charge_point_id=F("meter__charge_point__pk"))
            .annotate(current_index=F("extracted_energy"), current_index_date=F("reading_date"))
            .annotate(prev_index=Coalesce(prev_index, F("meter__initial_index")))
            .annotate(prev_index_date=Coalesce(prev_index_date, F("meter__initial_index_date")))
            .filter(meter__charge_point__is_deleted=False, meter__charge_point__is_article_2=False)
            .order_by("meter", "reading_date")
        )


class ElecMeterReading(models.Model):
    objects = models.Manager()
    extended_objects = ExtendedMeterReadingManager()

    class Meta:
        db_table = "elec_meter_reading"
        verbose_name = "Relevé de point de recharge"
        verbose_name_plural = "Relevés de points de recharge"

    extracted_energy = models.FloatField(null=True, blank=True)  # unit = kWh
    reading_date = models.DateField()
    cpo = models.ForeignKey(Entity, on_delete=models.deletion.CASCADE, related_name="elec_meter_readings")
    application = models.ForeignKey(
        ElecMeterReadingApplication, on_delete=models.deletion.CASCADE, related_name="elec_meter_readings"
    )
    meter = models.ForeignKey(
        ElecMeter, on_delete=models.CASCADE, null=True, blank=False, related_name="elec_meter_readings"
    )
    enr_ratio = models.FloatField(null=True, blank=True)
    operating_unit = models.CharField(max_length=64, null=True, blank=True)

    @property
    def charge_point(self):
        return self.meter.charge_point if self.meter else None

    @property
    def charge_point_id(self):
        return self.charge_point.id if self.charge_point else None

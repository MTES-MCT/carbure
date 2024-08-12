from django.db import models

from core.models import Entity
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from elec.models.elec_meter import ElecMeter


class ElecMeterReading(models.Model):
    class Meta:
        db_table = "elec_meter_reading"
        verbose_name = "Relevé de point de recharge"
        verbose_name_plural = "Relevés de points de recharge"

    extracted_energy = models.FloatField(null=True, blank=True)
    renewable_energy = models.FloatField(null=True, blank=True)
    reading_date = models.DateField()
    cpo = models.ForeignKey(Entity, on_delete=models.deletion.CASCADE, related_name="elec_meter_readings")
    application = models.ForeignKey(ElecMeterReadingApplication, on_delete=models.deletion.CASCADE, related_name="elec_meter_readings")  # fmt:skip
    meter = models.ForeignKey(ElecMeter, on_delete=models.CASCADE, null=True, blank=False, related_name="elec_meter_readings")  # fmt:skip

    @property
    def charge_point(self):
        return self.meter.charge_point if self.meter else None

    @property
    def charge_point_id(self):
        return self.charge_point.id if self.charge_point else None

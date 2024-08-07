from django.db import models

from core.models import Entity
from elec.models.elec_charge_point import ElecChargePoint
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
    charge_point = models.ForeignKey(ElecChargePoint, on_delete=models.deletion.CASCADE, related_name="elec_meter_readings")
    cpo = models.ForeignKey(Entity, on_delete=models.deletion.CASCADE, related_name="elec_meter_readings")
    application = models.ForeignKey(ElecMeterReadingApplication, on_delete=models.deletion.CASCADE, related_name="elec_meter_readings")  # fmt:skip
    meter = models.ForeignKey(ElecMeter, on_delete=models.CASCADE, null=True, blank=False, related_name="elec_meter_readings")  # fmt:skip

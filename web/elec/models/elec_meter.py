from django.db import models
from simple_history.models import HistoricalRecords

from elec.models.elec_charge_point import ElecChargePoint


class ElecMeter(models.Model):
    mid_certificate = models.CharField(max_length=128, null=False, blank=False)
    initial_index = models.FloatField(null=True, blank=False)
    initial_index_date = models.DateField(null=True, blank=False)
    charge_point = models.ForeignKey(
        ElecChargePoint, null=True, blank=False, on_delete=models.CASCADE, related_name="elec_meters"
    )
    history = HistoricalRecords(
        custom_model_name="ElecMeterHistory",
        table_name="elec_meter_history",
        history_change_reason_field=models.CharField(max_length=100, null=True),
        verbose_name="Historique compteur électrique",
        verbose_name_plural="Historiques des compteurs électriques",
        cascade_delete_history=True,
    )

    class Meta:
        db_table = "elec_meter"
        verbose_name = "Compteur électrique d'un point de charge"
        verbose_name_plural = "Compteurs électriques des points de charge"

    def __str__(self):
        return self.mid_certificate

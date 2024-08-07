from django.db import models

from elec.models.elec_charge_point import ElecChargePoint


class ElecMeter(models.Model):
    mid_certificate = models.CharField(max_length=128, null=False, blank=False)
    initial_index = models.FloatField(null=True, blank=False)
    initial_index_date = models.DateField(null=True, blank=False)
    charge_point = models.ForeignKey(ElecChargePoint, null=True, blank=False, on_delete=models.SET_NULL, related_name="elec_meters")  # fmt:skip

    class Meta:
        db_table = "elec_meter"
        verbose_name = "Compteur électrique d'un point de charge"
        verbose_name_plural = "Compteurs électriques des points de charge"

    def __str__(self):
        return self.mid_certificate

from django.db import models
from core.models import Entity

from elec.models.elec_charge_point_application import ElecChargePointApplication


class ElecChargePoint(models.Model):
    class Meta:
        db_table = "elec_charge_point"
        verbose_name = "Point de recharge"
        verbose_name_plural = "Points de recharge"

    AC = "AC"
    DC = "DC"

    # related
    application = models.ForeignKey(ElecChargePointApplication, on_delete=models.deletion.CASCADE, related_name="elec_charge_points")  # fmt:skip
    cpo = models.ForeignKey(Entity, on_delete=models.deletion.CASCADE, related_name="elec_charge_points")

    # cpo excel data
    charge_point_id = models.CharField(max_length=64)
    current_type = models.CharField(max_length=2, choices=[(AC, "Courant alternatif"), (DC, "Courant continu")])
    installation_date = models.DateField()
    mid_id = models.CharField(max_length=64, null=True, blank=True)
    measure_date = models.DateField(null=True, blank=True)
    measure_energy = models.FloatField(null=True, blank=True)
    is_article_2 = models.BooleanField(default=False)
    is_auto_consumption = models.BooleanField(default=False)
    is_article_4 = models.BooleanField(default=False)
    measure_reference_point_id = models.CharField(max_length=64)

    # transport.data.gouv.fr data
    station_name = models.CharField(max_length=64)
    station_id = models.CharField(max_length=64)
    nominal_power = models.FloatField(null=True, blank=True)
    cpo_name = models.CharField(max_length=64, null=True, blank=True)
    cpo_siren = models.CharField(max_length=64, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

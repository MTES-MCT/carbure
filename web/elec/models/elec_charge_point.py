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
    CURRENT_TYPES = [(AC, "Courant alternatif"), (DC, "Courant continu")]

    # related
    application = models.ForeignKey(ElecChargePointApplication, on_delete=models.deletion.CASCADE, related_name="elec_charge_points")  # fmt:skip
    cpo = models.ForeignKey(Entity, on_delete=models.deletion.CASCADE, related_name="elec_charge_points")
    previous_version = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="next_version")  # fmt:skip

    # cpo excel data
    charge_point_id = models.CharField(max_length=64)
    current_type = models.CharField(max_length=2, choices=CURRENT_TYPES)
    installation_date = models.DateField()
    mid_id = models.CharField(max_length=128, null=True, blank=True)
    measure_date = models.DateField(null=True, blank=True)
    measure_energy = models.FloatField(null=True, blank=True)
    is_article_2 = models.BooleanField(default=False)
    measure_reference_point_id = models.CharField(max_length=64, null=True, blank=True)

    # transport.data.gouv.fr data
    station_name = models.CharField(max_length=128)
    station_id = models.CharField(max_length=64)
    nominal_power = models.FloatField(null=True, blank=True)
    cpo_name = models.CharField(max_length=64, null=True, blank=True)
    cpo_siren = models.CharField(max_length=64, null=True, blank=True)
    latitude = models.DecimalField(max_digits=18, decimal_places=15, null=True, blank=True)
    longitude = models.DecimalField(max_digits=18, decimal_places=15, null=True, blank=True)

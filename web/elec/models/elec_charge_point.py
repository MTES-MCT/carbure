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
    lne_certificate = models.CharField(max_length=64, null=True, blank=True)
    meter_reading_date = models.DateField(null=True, blank=True)
    meter_reading_energy = models.FloatField(null=True, blank=True)
    is_using_reference_meter = models.BooleanField(default=False)
    is_auto_consumption = models.BooleanField(default=False)
    has_article_4_regularization = models.BooleanField(default=False)
    reference_meter_id = models.CharField(max_length=64)

    # transport.data.gouv.fr data
    station_name = models.CharField(max_length=64)
    station_id = models.CharField(max_length=64)

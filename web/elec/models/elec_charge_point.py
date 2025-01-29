from django.db import models
from simple_history.models import HistoricalRecords

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
    application = models.ForeignKey(
        ElecChargePointApplication, on_delete=models.deletion.CASCADE, related_name="elec_charge_points"
    )
    cpo = models.ForeignKey(Entity, on_delete=models.deletion.CASCADE, related_name="elec_charge_points")
    current_meter = models.ForeignKey(
        "ElecMeter", on_delete=models.SET_NULL, null=True, blank=True, related_name="elec_charge_points"
    )

    # cpo excel data
    charge_point_id = models.CharField(max_length=64)
    current_type = models.CharField(max_length=2, choices=CURRENT_TYPES)
    installation_date = models.DateField()
    is_article_2 = models.BooleanField(default=False)
    measure_reference_point_id = models.CharField(max_length=64, null=True, blank=True)

    # transport.data.gouv.fr data
    station_name = models.CharField(max_length=128)
    station_id = models.CharField(max_length=64)
    nominal_power = models.FloatField(null=True, blank=True)
    cpo_name = models.CharField(max_length=128, null=True, blank=True)
    cpo_siren = models.CharField(max_length=64, null=True, blank=True)
    latitude = models.DecimalField(max_digits=18, decimal_places=15, null=True, blank=True)
    longitude = models.DecimalField(max_digits=18, decimal_places=15, null=True, blank=True)

    is_deleted = models.BooleanField(default=False)
    history = HistoricalRecords(
        custom_model_name="ElecChargePointHistory",
        table_name="elec_charge_point_history",
        history_change_reason_field=models.CharField(max_length=100, null=True),
        verbose_name="Historique point de recharge",
        verbose_name_plural="Historiques des points de recharge",
        cascade_delete_history=True,
    )

    @property
    def mid_id(self):
        return self.current_meter.mid_certificate if self.current_meter else None

    @property
    def measure_date(self):
        if self.current_meter:
            if self.current_meter.elec_meter_readings.all():
                return self.current_meter.elec_meter_readings.order_by("-reading_date").first().reading_date
            else:
                return self.current_meter.initial_index_date
        else:
            return None

    @property
    def measure_energy(self):
        if self.current_meter:
            if self.current_meter.elec_meter_readings.all():
                return self.current_meter.elec_meter_readings.order_by("-reading_date").first().extracted_energy
            else:
                return self.current_meter.initial_index
        else:
            return None

    @property
    def initial_index(self):
        return self.current_meter.initial_index if self.current_meter else None

    @property
    def initial_index_date(self):
        return self.current_meter.initial_index_date if self.current_meter else None

    def is_updatable(self):
        return self.application.status != ElecChargePointApplication.AUDIT_IN_PROGRESS

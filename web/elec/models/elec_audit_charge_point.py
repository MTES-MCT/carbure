from django.db import models

from elec.models.elec_audit_sample import ElecAuditSample
from elec.models.elec_charge_point import ElecChargePoint
from elec.models.elec_meter_reading import ElecMeterReading


class ElecAuditChargePoint(models.Model):
    class Meta:
        db_table = "elec_audit_charge_point"
        verbose_name = "Point de recharge audité"
        verbose_name_plural = "Points de recharge audités"

    audit_sample = models.ForeignKey(
        ElecAuditSample, on_delete=models.deletion.CASCADE, related_name="audited_charge_points"
    )

    is_auditable = models.BooleanField(null=True, blank=True)
    current_type = models.CharField(max_length=2, null=True, blank=True, choices=ElecChargePoint.CURRENT_TYPES)
    observed_mid_or_prm_id = models.CharField(max_length=128, null=True, blank=True)
    observed_energy_reading = models.FloatField(null=True, blank=True)
    has_dedicated_pdl = models.BooleanField(null=True, blank=True)
    audit_date = models.DateField(null=True, blank=True)
    comment = models.CharField(max_length=512, default="")

    charge_point = models.ForeignKey(
        ElecChargePoint, on_delete=models.deletion.CASCADE, null=True, blank=True, related_name="charge_point_audit"
    )
    meter_reading = models.ForeignKey(
        ElecMeterReading, on_delete=models.deletion.CASCADE, null=True, blank=True, related_name="meter_reading_audit"
    )

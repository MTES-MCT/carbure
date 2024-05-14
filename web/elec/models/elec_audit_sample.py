from django.db import models

from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication


class ElecAuditSample(models.Model):
    class Meta:
        db_table = "elec_audit_sample"
        verbose_name = "Echantillon de points de recharge audités"
        verbose_name_plural = "Echantillons de points de recharge audités"

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    AUDITED = "AUDITED"
    STATUSES = [
        (PENDING, PENDING),
        (IN_PROGRESS, IN_PROGRESS),
        (AUDITED, AUDITED),
    ]

    status = models.CharField(max_length=32, default=PENDING, choices=STATUSES)
    created_at = models.DateField(auto_now_add=True)
    charge_point_application = models.ForeignKey(ElecChargePointApplication, on_delete=models.deletion.CASCADE, null=True, blank=True, related_name="audit_sample")  # fmt:skip
    meter_reading_application = models.ForeignKey(ElecMeterReadingApplication, on_delete=models.deletion.CASCADE, null=True, blank=True, related_name="audit_sample")  # fmt:skip

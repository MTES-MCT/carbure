from django.db import models

from core.models import Entity
from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication


class ElecAuditSample(models.Model):
    class Meta:
        db_table = "elec_audit_sample"
        verbose_name = "Echantillon de points de recharge audités"
        verbose_name_plural = "Echantillons de points de recharge audités"

    IN_PROGRESS = "IN_PROGRESS"
    AUDITED = "AUDITED"
    STATUSES = [
        (IN_PROGRESS, IN_PROGRESS),
        (AUDITED, AUDITED),
    ]

    status = models.CharField(max_length=32, default=IN_PROGRESS, choices=STATUSES)
    percentage = models.IntegerField(default=0)
    created_at = models.DateField(auto_now_add=True)
    charge_point_application = models.ForeignKey(ElecChargePointApplication, on_delete=models.deletion.CASCADE, null=True, blank=True, related_name="audit_sample")  # fmt:skip
    meter_reading_application = models.ForeignKey(ElecMeterReadingApplication, on_delete=models.deletion.CASCADE, null=True, blank=True, related_name="audit_sample")  # fmt:skip
    cpo = models.ForeignKey(Entity, related_name="elec_audited_applications", on_delete=models.deletion.CASCADE, null=True, blank=True)  # fmt:skip
    auditor = models.ForeignKey(Entity, related_name="elec_audits", on_delete=models.deletion.CASCADE, null=True, blank=True)  # fmt:skip

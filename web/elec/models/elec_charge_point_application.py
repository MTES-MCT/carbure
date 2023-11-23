from django.db import models

from core.models import Entity


class ElecChargePointApplication(models.Model):
    class Meta:
        db_table = "elec_charge_point_application"
        verbose_name = "Inscription points de recharge"
        verbose_name_plural = "Inscriptions points de recharge"

    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    STATUSES = [(PENDING, PENDING), (ACCEPTED, ACCEPTED), (REJECTED, REJECTED)]

    status = models.CharField(max_length=10, default=PENDING, choices=STATUSES)
    created_at = models.DateTimeField(auto_now_add=True)
    cpo = models.ForeignKey(Entity, on_delete=models.deletion.CASCADE, related_name="elec_charge_point_applications")

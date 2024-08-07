from django.db import models

from core.models import Entity


class ElecMeterReadingApplication(models.Model):
    class Meta:
        db_table = "elec_meter_reading_application"
        verbose_name = "Inscription de relevés de points de recharge"
        verbose_name_plural = "Inscriptions de relevés de points de recharge"

    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    AUDIT_IN_PROGRESS = "AUDIT_IN_PROGRESS"
    AUDIT_DONE = "AUDIT_DONE"

    STATUSES = [
        (PENDING, PENDING),
        (ACCEPTED, ACCEPTED),
        (REJECTED, REJECTED),
        (AUDIT_IN_PROGRESS, AUDIT_IN_PROGRESS),
        (AUDIT_DONE, AUDIT_DONE),
    ]

    # niveaux d'urgence d'une déclaration par rapport à la date de dépôt et les deadlines
    LOW = "LOW"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    QUARTERS = (
        (1, "T1"),
        (2, "T2"),
        (3, "T3"),
        (4, "T4"),
    )

    status = models.CharField(max_length=32, default=PENDING, choices=STATUSES)
    quarter = models.IntegerField(choices=QUARTERS)
    year = models.IntegerField()
    created_at = models.DateField(auto_now_add=True)
    cpo = models.ForeignKey(Entity, on_delete=models.deletion.CASCADE, related_name="elec_meter_reading_applications")

from django.db import models
from django.db.models import Count, Q, Sum

from core.models import Entity


class ElecChargePointApplicationManager(models.Manager):
    # get_annotated_applications and get_annotated_applications_by_cpo
    def get_annotated_applications(self):
        return self.get_queryset().annotate(
            station_count=Count(
                "elec_charge_points__station_id",
                filter=Q(elec_charge_points__is_deleted=False),
                distinct=True,
            ),
            charge_point_count=Count("elec_charge_points__id", filter=Q(elec_charge_points__is_deleted=False)),
            power_total=Sum(
                "elec_charge_points__nominal_power",
                filter=Q(elec_charge_points__is_deleted=False),
            ),
        )


class ElecChargePointApplication(models.Model):
    objects = ElecChargePointApplicationManager()

    class Meta:
        db_table = "elec_charge_point_application"
        verbose_name = "Inscription points de recharge"
        verbose_name_plural = "Inscriptions points de recharge"

    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    AUDIT_IN_PROGRESS = "AUDIT_IN_PROGRESS"
    AUDIT_DONE = "AUDIT_DONE"
    STATUSES = [
        (PENDING, PENDING),
        (ACCEPTED, ACCEPTED),
        (REJECTED, REJECTED),
        (AUDIT_DONE, AUDIT_DONE),
        (AUDIT_IN_PROGRESS, AUDIT_IN_PROGRESS),
    ]

    status = models.CharField(max_length=32, default=PENDING, choices=STATUSES)
    created_at = models.DateField(auto_now_add=True)
    cpo = models.ForeignKey(
        Entity,
        on_delete=models.deletion.CASCADE,
        related_name="elec_charge_point_applications",
    )

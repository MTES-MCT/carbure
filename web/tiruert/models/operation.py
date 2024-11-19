from django.db import models

from core.models import MatierePremiere


class Operation(models.Model):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    DELETED = "DELETED"
    OPERATION_STATUSES = (
        (PENDING, PENDING),
        (ACCEPTED, ACCEPTED),
        (REJECTED, REJECTED),
        (DELETED, DELETED),
    )

    BLENDING = "BLENDING"  # Incorporation
    TRADING = "TRADING"  # Cession
    TENEUR = "TENEUR"  # Teneur
    OPERATION_TYPES = (
        (BLENDING, BLENDING),
        (TRADING, TRADING),
        (TENEUR, TENEUR),
    )

    type = models.CharField(max_length=12, choices=OPERATION_TYPES)
    status = models.CharField(max_length=12, choices=OPERATION_STATUSES, default=PENDING)
    customs_category = models.CharField(max_length=32, choices=MatierePremiere.MP_CATEGORIES, default=MatierePremiere.CONV)
    biofuel = models.ForeignKey("core.Biocarburant", null=True, blank=False, on_delete=models.SET_NULL)
    from_entity = models.ForeignKey(
        "core.Entity", null=True, on_delete=models.deletion.CASCADE, related_name="from_operations"
    )
    to_entity = models.ForeignKey("core.Entity", null=True, on_delete=models.deletion.CASCADE, related_name="to_operations")
    depot = models.ForeignKey("transactions.Depot", null=True, on_delete=models.SET_NULL, related_name="operations")
    created_at = models.DateTimeField(auto_now_add=True)
    validity_date = models.DateField(null=False, blank=False)

    class Meta:
        db_table = "tiruert_operations"
        verbose_name = "Opération"
        verbose_name_plural = "Opérations"

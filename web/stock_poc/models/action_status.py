from django.db import models


class ActionStatus(models.Model):
    # Status of an action (can also be null = no workflow status yet)
    ACCEPTED = "ACCEPTED"
    REFUSED = "REFUSED"
    PENDING = "PENDING"
    STATUSES = [
        (ACCEPTED, ACCEPTED),
        (REFUSED, REFUSED),
        (PENDING, PENDING),
    ]

    status = models.CharField(max_length=16, choices=STATUSES, null=True, blank=True, verbose_name="Statut")
    created_at = models.DateTimeField(auto_now_add=True)
    action = models.ForeignKey(
        "stock_poc.Action", on_delete=models.CASCADE, related_name="action_statuses", verbose_name="Action"
    )

    class Meta:
        db_table = "stock_poc_action_status"
        verbose_name = "Statut d'action"
        verbose_name_plural = "Statuts d'action"
        ordering = ["id"]

from django.db import models
from django.db.models import OuterRef, Subquery


class ActionStatus(models.Model):
    # Status of an action (can also be null = no workflow status yet)
    CREATED = "CREATED"
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    BLOCKED = "BLOCKED"
    DELETED = "DELETED"
    STATUSES = [
        (CREATED, CREATED),
        (PENDING, PENDING),
        (ACCEPTED, ACCEPTED),
        (REJECTED, REJECTED),
        (BLOCKED, BLOCKED),
        (DELETED, DELETED),
    ]

    status = models.CharField(choices=STATUSES, max_length=16, verbose_name="Statut")
    created_at = models.DateTimeField(auto_now_add=True)
    action = models.ForeignKey(
        "traceability.Action", on_delete=models.CASCADE, related_name="action_statuses", verbose_name="Action"
    )

    class Meta:
        db_table = "action_status"
        verbose_name = "Statut d'action"
        verbose_name_plural = "Statuts d'action"
        ordering = ["id"]
        indexes = [
            models.Index(fields=["action", "-created_at", "-id"], name="action_status_latest"),
        ]


def latest_status():
    """Subquery for an action's current status: newest row, then highest id."""
    return Subquery(ActionStatus.objects.filter(action=OuterRef("id")).order_by("-created_at", "-id").values("status")[:1])

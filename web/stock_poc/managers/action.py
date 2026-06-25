from decimal import Decimal

from django.db import models
from django.db.models import DecimalField, F, OuterRef, Subquery, Sum
from django.db.models.functions import Coalesce

from stock_poc.models.action_status import ActionStatus


def _latest_status_subquery(*, action_outer_ref: str = "id"):
    return ActionStatus.objects.filter(action=OuterRef(action_outer_ref)).order_by("-created_at", "-id")


def _reserved_children_quantity_subquery(*, parent_outer_ref: str = "id"):
    """Sum of direct children quantities whose latest status is not REFUSED."""
    from stock_poc.models import Action

    child_latest_status = _latest_status_subquery(action_outer_ref="pk")

    return (
        Action._base_manager.filter(parent=OuterRef(parent_outer_ref))
        .annotate(latest_status=Subquery(child_latest_status.values("status")[:1]))
        .exclude(latest_status=ActionStatus.REFUSED)
        .values("parent")
        .annotate(total=Sum("quantity"))
        .values("total")
    )


class ActionManager(models.Manager):
    def get_queryset(self):
        latest = _latest_status_subquery(action_outer_ref="id")
        reserved = _reserved_children_quantity_subquery(parent_outer_ref="id")

        return (
            super()
            .get_queryset()
            .prefetch_related("action_statuses")
            .annotate(status=Subquery(latest.values("status")[:1]))
            .annotate(status_updated_at=Subquery(latest.values("created_at")[:1]))
            .annotate(
                available=F("quantity")
                - Coalesce(
                    Subquery(reserved[:1], output_field=DecimalField(max_digits=20, decimal_places=2)),
                    Decimal("0"),
                    output_field=DecimalField(max_digits=20, decimal_places=2),
                )
            )
        )

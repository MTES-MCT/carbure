from decimal import Decimal

from django.db.models import DecimalField, ExpressionWrapper, F, OuterRef, Subquery, Sum, Value
from django.db.models.functions import Coalesce

from traceability.models.action_status import ActionStatus, latest_status

# A rejected or deleted child does not consume its parent.
_EXCLUDED_CHILD_STATUSES = (ActionStatus.DELETED, ActionStatus.REJECTED)
_QUANTITY = DecimalField(max_digits=16, decimal_places=3)


def quantity_available():
    """quantity minus the sum of direct children.

    Children whose latest status is DELETED or REJECTED are left out.
    Grandchildren do not. No consuming child leaves the stored quantity.
    """
    from traceability.models.action import Action

    consumed = (
        Action.unannotated.filter(parent_id=OuterRef("pk"))
        .annotate(status=latest_status())
        .exclude(status__in=_EXCLUDED_CHILD_STATUSES)
        .order_by()
        .values("parent_id")
        .annotate(total=Sum("quantity"))
        .values("total")
    )
    return ExpressionWrapper(
        F("quantity") - Coalesce(Subquery(consumed, output_field=_QUANTITY), Value(Decimal("0")), output_field=_QUANTITY),
        output_field=_QUANTITY,
    )

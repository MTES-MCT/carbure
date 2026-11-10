from django.db.models import Q, Sum

from traceability.models.action import Action
from traceability.models.action_status import ActionStatus

# A rejected or deleted child does not consume its parent. A missing status still does.
_EXCLUDED_CHILD_STATUSES = (ActionStatus.DELETED, ActionStatus.REJECTED)


def attach_quantity_available(actions: list) -> list:
    """Set quantity_available from the action's own quantity and its direct children.

    quantity_available = quantity - sum of direct children's quantities.
    Children whose current status is DELETED or REJECTED are left out.
    The value stays in the same unit as quantity. Only the given actions are
    aggregated, so pass the page or the detail row, not the whole table.
    """
    if not actions:
        return actions

    consumed_rows = (
        Action.objects.filter(parent_id__in=[action.pk for action in actions])
        .filter(Q(status__isnull=True) | ~Q(status__in=_EXCLUDED_CHILD_STATUSES))
        .values("parent_id")
        .annotate(consumed=Sum("quantity"))
    )
    consumed_by_parent = {row["parent_id"]: row["consumed"] for row in consumed_rows}
    for action in actions:
        action.quantity_available = action.quantity - consumed_by_parent.get(action.pk, 0)
    return actions

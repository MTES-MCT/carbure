from django.db import transaction
from django.db.models import QuerySet

from traceability.exceptions import NoEligibleActionError
from traceability.models import Action, ActionStatus


@transaction.atomic
def valorize(actions: QuerySet[Action]) -> list[Action]:
    """Create a VALORIZE child for each CONSUME action currently PENDING, then accept the CONSUME.

    The child keeps the parent's quantity and stores no material. The displayed unit
    is the nearest material on the parent chain, resolved when the action is read.
    Ineligible rows in `actions` are skipped.
    Raises NoEligibleActionError if none remain.
    """
    pending_consumes = list(actions.filter(type=Action.CONSUME, status=ActionStatus.PENDING))
    if not pending_consumes:
        raise NoEligibleActionError()

    children = Action.bulk_create(
        [
            Action(
                type=Action.VALORIZE,
                holder=action.holder,
                industry=action.industry,
                working_date=action.working_date,
                quantity=action.quantity,
                parent=action,
                material=None,
            )
            for action in pending_consumes
        ]
    )
    ActionStatus.objects.bulk_create(
        ActionStatus(status=ActionStatus.ACCEPTED, action=action) for action in pending_consumes
    )
    return list(children)

import uuid

from django.db import transaction
from django.db.models import QuerySet

from traceability.exceptions import NoEligibleActionError
from traceability.models import Action, ActionStatus


@transaction.atomic
def valorize(actions: QuerySet[Action]) -> list[Action]:
    """Create a VALORIZE child for each INIT action currently PENDING, then accept the INIT.

    Ineligible rows in `actions` are skipped. Raises NoEligibleActionError if none remain.
    """
    pending_inits = list(actions.filter(type=Action.INIT, status=ActionStatus.PENDING))
    if not pending_inits:
        raise NoEligibleActionError()

    children = Action.bulk_create(
        [
            Action(
                pos_id=str(uuid.uuid4()),
                type=Action.VALORIZE,
                holder=action.holder,
                industry=action.industry,
                working_date=action.working_date,
                quantity=action.quantity,
                parent=action,
            )
            for action in pending_inits
        ]
    )
    ActionStatus.objects.bulk_create(ActionStatus(status=ActionStatus.ACCEPTED, action=action) for action in pending_inits)
    return list(children)

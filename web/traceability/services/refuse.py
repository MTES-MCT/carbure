from django.db import transaction
from django.db.models import QuerySet

from traceability.exceptions import NoEligibleActionError
from traceability.models import Action, ActionStatus


@transaction.atomic
def refuse(actions: QuerySet[Action]) -> list[Action]:
    """Create a REJECTED status for each INIT action currently PENDING.

    Ineligible rows in `actions` are skipped. Raises NoEligibleActionError if none remain.
    """
    pending_inits = list(actions.filter(type=Action.INIT, status=ActionStatus.PENDING))
    if not pending_inits:
        raise NoEligibleActionError()

    ActionStatus.objects.bulk_create(ActionStatus(status=ActionStatus.REJECTED, action=action) for action in pending_inits)
    return pending_inits

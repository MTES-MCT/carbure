from django.db import transaction
from django.db.models import QuerySet

from traceability.exceptions import NoEligibleActionError
from traceability.models import Action, ActionStatus


@transaction.atomic
def refuse(actions: QuerySet[Action]) -> list[Action]:
    """Create a REJECTED status for each CONSUME action currently PENDING.

    Ineligible rows in `actions` are skipped. Raises NoEligibleActionError if none remain.
    """
    pending_consumes = list(actions.filter(type=Action.CONSUME, status=ActionStatus.PENDING))
    if not pending_consumes:
        raise NoEligibleActionError()

    ActionStatus.objects.bulk_create(
        ActionStatus(status=ActionStatus.REJECTED, action=action) for action in pending_consumes
    )
    return pending_consumes

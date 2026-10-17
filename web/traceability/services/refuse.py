from django.db import transaction
from django.db.models import QuerySet

from traceability.exceptions import NoEligibleActionError
from traceability.lifecycle.checks import actions_that_can_change_status
from traceability.models import Action, ActionStatus


@transaction.atomic
def refuse(actions: QuerySet[Action]) -> list[Action]:
    """Reject each action the matrix lets reach REJECTED.

    The permission on the transition is not checked. Ineligible rows are skipped.
    Raises NoEligibleActionError if none remain.
    """
    eligible = actions_that_can_change_status(actions, ActionStatus.REJECTED)
    if not eligible:
        raise NoEligibleActionError()

    ActionStatus.objects.bulk_create(ActionStatus(status=ActionStatus.REJECTED, action=action) for action in eligible)
    return eligible

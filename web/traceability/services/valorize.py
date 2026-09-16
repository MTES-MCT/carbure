import uuid

from django.db import transaction
from django.db.models import QuerySet

from traceability.exceptions import ConversionError, NoEligibleActionError
from traceability.models import Action, ActionStatus


@transaction.atomic
def valorize(actions: QuerySet[Action]) -> list[Action]:
    """Create a VALORIZE child in MJ for each INIT action currently PENDING, then accept the INIT.

    Child quantity is the parent's energy. Ineligible rows in `actions` are skipped.
    Raises NoEligibleActionError if none remain, ConversionError if energy cannot be derived.
    """
    pending_inits = list(actions.filter(type=Action.INIT, status=ActionStatus.PENDING))
    if not pending_inits:
        raise NoEligibleActionError()

    missing_energy = [action for action in pending_inits if action.energy is None]
    if missing_energy:
        raise ConversionError(missing_energy)

    children = Action.bulk_create(
        [
            Action(
                pos_id=str(uuid.uuid4()),
                type=Action.VALORIZE,
                unit=Action.MJ,
                holder=action.holder,
                industry=action.industry,
                working_date=action.working_date,
                quantity=action.energy,
                parent=action,
            )
            for action in pending_inits
        ]
    )
    ActionStatus.objects.bulk_create(ActionStatus(status=ActionStatus.ACCEPTED, action=action) for action in pending_inits)
    return list(children)

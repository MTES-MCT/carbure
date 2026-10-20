import uuid

from django.db import transaction
from django.db.models import QuerySet

from traceability.exceptions import ConversionError, NoEligibleActionError
from traceability.models import Action, ActionStatus, Material


@transaction.atomic
def valorize(actions: QuerySet[Action]) -> list[Action]:
    """Create a VALORIZE child for each INIT action currently PENDING, then accept the INIT.

    Child quantity is the parent's energy. The child material is VALORIZED_ENERGY (unit MJ),
    so the stored quantity is displayed in MJ. That material has no conversion factors.
    Ineligible rows in `actions` are skipped.
    Raises NoEligibleActionError if none remain, ConversionError if energy cannot be derived.
    """
    pending_inits = list(actions.filter(type=Action.INIT, status=ActionStatus.PENDING))
    if not pending_inits:
        raise NoEligibleActionError()

    missing_energy = [action for action in pending_inits if action.energy is None]
    if missing_energy:
        raise ConversionError(missing_energy)

    energy_material = Material.valorized_energy()
    children = Action.bulk_create(
        [
            Action(
                pos_id=str(uuid.uuid4()),
                type=Action.VALORIZE,
                holder=action.holder,
                industry=action.industry,
                working_date=action.working_date,
                quantity=action.energy,
                parent=action,
                material=energy_material,
            )
            for action in pending_inits
        ]
    )
    ActionStatus.objects.bulk_create(ActionStatus(status=ActionStatus.ACCEPTED, action=action) for action in pending_inits)
    return list(children)

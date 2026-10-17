import uuid

from django.db import transaction
from django.db.models import QuerySet

from traceability.exceptions import ConversionError, NoEligibleActionError
from traceability.lifecycle.checks import actions_that_can_change_status
from traceability.models import Action, ActionStatus, Material


@transaction.atomic
def valorize(actions: QuerySet[Action]) -> list[Action]:
    """Accept each action the matrix lets reach ACCEPTED, then create a VALORIZE child.

    Child quantity is the parent's energy. The child material is VALORIZED_ENERGY (unit MJ),
    so the stored quantity is displayed in MJ. That material has no conversion factors.
    The permission on the transition is not checked. Ineligible rows are skipped.
    Raises NoEligibleActionError if none remain, ConversionError if energy cannot be derived.
    """
    eligible = actions_that_can_change_status(actions, ActionStatus.ACCEPTED)
    if not eligible:
        raise NoEligibleActionError()

    missing_energy = [action for action in eligible if action.energy is None]
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
            for action in eligible
        ]
    )
    ActionStatus.objects.bulk_create(ActionStatus(status=ActionStatus.ACCEPTED, action=action) for action in eligible)
    return list(children)

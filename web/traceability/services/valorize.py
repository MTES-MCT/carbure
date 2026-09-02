import uuid

from django.db import transaction
from django.db.models import QuerySet

from traceability.models import Action, ActionStatus


def valorize(actions: QuerySet[Action]):
    # Only actions of type INIT and with status PENDING can be valorized (only for H2-v0)
    valorizable_actions = actions.filter(type__in=[Action.INIT], status__in=[ActionStatus.PENDING])

    if not valorizable_actions.exists():
        raise Exception("Aucune action éligible à valoriser")

    new_actions = []
    updated_action_statuses = []

    for action in valorizable_actions:
        new_actions.append(
            Action(
                pos_id=str(uuid.uuid4()),
                type=Action.VALORIZE,
                holder=action.holder,
                industry=action.industry,
                working_date=action.working_date,
                quantity=action.quantity,
                parent=action,
            )
        )

        updated_action_statuses.append(ActionStatus(status=ActionStatus.ACCEPTED, action=action))

    with transaction.atomic():
        Action.bulk_create(new_actions)
        ActionStatus.objects.bulk_create(updated_action_statuses)

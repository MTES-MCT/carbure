from traceability.exceptions import ActionNotDeletableError
from traceability.models import Action, ActionStatus


def delete_action(action: Action) -> None:
    """Hard-delete an INIT action whose current status is pending or rejected."""
    if action.type != Action.INIT or action.status not in (ActionStatus.PENDING, ActionStatus.REJECTED):
        raise ActionNotDeletableError()
    action.delete()

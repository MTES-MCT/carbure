from traceability.handlers.action import ActionIndustryHandler
from traceability.lifecycle.rules import Creation, Transition
from traceability.models import Action


def can_change_status(
    handler: ActionIndustryHandler, action_type: str, from_status: str, to_status: str
) -> Transition | None:
    """Return the transition allowed by this handler, or None.

    The permission stored on the transition is not called here.
    """
    for transition in handler.transitions:
        if (
            transition.action_type == action_type
            and transition.from_status == from_status
            and transition.to_status == to_status
        ):
            return transition
    return None


def can_create(handler: ActionIndustryHandler, action_type: str, parent: Action | None = None) -> Creation | None:
    """Return the creation allowed by this handler, or None.

    Without a parent, only a root creation matches.
    With a parent, its type and current status must match a Parent row.
    """
    for creation in handler.creations:
        if creation.action_type != action_type:
            continue
        if parent is None:
            if creation.root:
                return creation
            continue
        if any(rule.action_type == parent.type and rule.status == parent.status for rule in creation.parents):
            return creation
    return None

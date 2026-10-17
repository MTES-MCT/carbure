from traceability.handlers.action import ActionIndustryHandler
from traceability.handlers.registry import get_action_handler
from traceability.lifecycle.rules import Creation, Transition


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


def can_create(handler: ActionIndustryHandler, action_type: str, parent_type: str | None = None) -> Creation | None:
    """Return the creation allowed by this handler, or None."""
    for creation in handler.creations:
        # First : find the correct action type
        if creation.action_type != action_type:
            continue

        # Then : check if the creation is allowed when there is no parent
        if parent_type is None and creation.root:
            return creation

        # Then : check if the creation is allowed when there is a parent
        if parent_type is not None and parent_type in creation.parents:
            return creation
    return None


def actions_that_can_change_status(actions, to_status: str) -> list:
    """Actions whose industry matrix allows the current status to become `to_status`.

    The permission stored on the transition is not called.
    """
    eligible = []
    for action in actions:
        handler = get_action_handler(action.industry)
        if can_change_status(handler, action.type, action.status, to_status):
            eligible.append(action)
    return eligible

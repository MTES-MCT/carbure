from traceability.handlers.action import ActionIndustryHandler
from traceability.lifecycle.rules import Transition


def can_change_status(
    handler: ActionIndustryHandler, action_type: str, from_status: str, to_status: str
) -> Transition | None:
    """Return the transition allowed by this handler, or None."""
    for transition in handler.transitions:
        if (
            transition.action_type == action_type
            and transition.from_status == from_status
            and transition.to_status == to_status
        ):
            return transition
    return None

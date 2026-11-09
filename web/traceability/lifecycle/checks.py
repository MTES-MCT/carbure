from traceability.handlers.action import ActionIndustryHandler
from traceability.lifecycle.rules import ActionFlowEdge, Transition
from traceability.models import Action


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


def can_create(handler: ActionIndustryHandler, action_type: str, parent: Action | None = None) -> ActionFlowEdge | None:
    """Return the matching flow edge, without evaluating its authorization rule."""
    parent_state = (parent.type, parent.status) if parent is not None else None
    for edge in handler.action_flow:
        source, (child_type, _), _ = edge
        if source == parent_state and child_type == action_type:
            return edge
    return None

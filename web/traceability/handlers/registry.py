from h2.handlers import H2ActionHandler
from traceability.models import Action

from .action import ActionIndustryHandler

ACTION_HANDLERS: dict[str, type[ActionIndustryHandler]] = {
    Action.H2: H2ActionHandler,
}


def get_action_handler(industry: str) -> ActionIndustryHandler:
    try:
        return ACTION_HANDLERS[industry]()
    except KeyError as exc:
        raise ValueError(f"No action handler registered for industry {industry!r}") from exc

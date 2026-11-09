from collections.abc import Callable
from dataclasses import dataclass

ActionFlowEdge = tuple[tuple[str, str] | None, tuple[str, str], Callable | None]


class Rule:
    def is_allowed(self) -> bool:
        return True


@dataclass(frozen=True)
class Transition(Rule):
    """A status change allowed for one action type."""

    action_type: str
    from_status: str
    to_status: str

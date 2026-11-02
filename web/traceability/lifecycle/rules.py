from dataclasses import dataclass


class Rule:
    def is_allowed(self) -> bool:
        return True


@dataclass(frozen=True)
class Transition(Rule):
    """A status change allowed for one action type."""

    action_type: str
    from_status: str
    to_status: str


@dataclass(frozen=True)
class Creation(Rule):
    """Where an action type is allowed to be born, and in which status.

    A root line has no parent. Any other line names exactly one parent type
    and the status that parent must currently have.
    """

    action_type: str
    status: str
    root: bool = False
    parent: str | None = None
    parent_status: str | None = None

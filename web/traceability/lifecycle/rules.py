from dataclasses import dataclass

from rest_framework.permissions import BasePermission


@dataclass(frozen=True)
class Transition:
    """A status change allowed for one action type.

    permission is the class checked later, when an endpoint asks for the change.
    """

    action_type: str
    from_status: str
    to_status: str
    permission: type[BasePermission]


@dataclass(frozen=True)
class Creation:
    """Where an action type is allowed to be born, and in which status.

    A root line has no parent. Any other line names exactly one parent type
    and the status that parent must currently have.
    """

    action_type: str
    status: str
    root: bool = False
    parent: str | None = None
    parent_status: str | None = None

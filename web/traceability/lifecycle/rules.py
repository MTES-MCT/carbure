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
    """Where an action type is allowed to be born."""

    action_type: str
    root: bool
    parents: tuple[str, ...] = ()

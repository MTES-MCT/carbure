"""Column groups carried by the parent-chain walk.

The walk lives in ``services/parent_chain.py``. This module lists what it can carry.
A group is ``start``, ``climb`` (same keys, same order) and an optional ``annotate``.
How to add a column, a filter or a group: ``traceability/docs/parent_chain.md``.
"""

from dataclasses import dataclass
from typing import Callable

from traceability.services.inherited_fields import inherited_annotation, inherited_climb, inherited_start
from traceability.services.total_emissions import emission_annotation, emission_climb, emission_start


@dataclass(frozen=True)
class ColumnGroup:
    """``climb`` must return the same keys as ``start``, in the same order."""

    start: Callable[[], dict]
    climb: Callable[..., dict]
    annotate: Callable[..., dict] | None = None


# The page loads these. A filter loads only the groups it names.
PAGE_COLUMN_GROUPS = ("emissions", "inherited_fields")

COLUMN_GROUPS = {
    "emissions": ColumnGroup(emission_start, emission_climb, emission_annotation),
    "inherited_fields": ColumnGroup(inherited_start, inherited_climb, inherited_annotation),
}

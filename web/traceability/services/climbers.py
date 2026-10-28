"""Columns carried by the parent-chain walk.

The walk itself lives in ``services/parent_chain.py``. It does not know these columns.
This module is the list of what the walk can carry.

A climber is three functions:

- ``start`` fills the columns on the action the walk starts from
- ``climb`` fills the same columns, in the same order, one parent higher.
  ``F(...)`` reads the parent row. ``cte.col.<name>`` reads the value carried so far.
- ``annotate`` copies the raw value onto the action so it can be published afterwards.
  Leave it empty when the column only exists to be filtered.

A value the front receives is a column of the ``inherited_fields`` climber
(``inherited_start``, ``inherited_climb``, ``inherited_annotation``), then a key
of ``attach_inherited_fields`` and of ``ActionInheritedFieldsSerializer``.
It does not get its own climber. ``PAGE_CLIMBERS`` already loads that climber.
To filter on one of those columns, subclass ``RecursiveColumnFilter`` in
``filters/recursive.py`` and set ``climber = "inherited_fields"``. When the query param
is set, the column filter calls ``RecursiveFilter``, which walks every selected column once.

A predicate such as "an ancestor has type INIT" is a climber whose column
becomes true and stays true (keep ``cte.col`` when it is already true, otherwise
read the parent). It is not another kind of walk.
"""

from dataclasses import dataclass
from typing import Callable

from traceability.services.inherited_fields import inherited_annotation, inherited_climb, inherited_start
from traceability.services.total_emissions import emission_annotation, emission_climb, emission_start


@dataclass(frozen=True)
class Climber:
    """``climb`` must return the same keys as ``start``, in the same order."""

    start: Callable[[], dict]
    climb: Callable[..., dict]
    annotate: Callable[..., dict] | None = None


# The page loads these. A filter loads only the climbers it names.
PAGE_CLIMBERS = ("emissions", "inherited_fields")

CLIMBERS = {
    "emissions": Climber(emission_start, emission_climb, emission_annotation),
    "inherited_fields": Climber(inherited_start, inherited_climb, inherited_annotation),
}

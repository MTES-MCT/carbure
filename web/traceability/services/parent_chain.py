"""Climb each action's parent chain once, up to the root.

GES sums and the inherited material id are contributions plugged into the same
recursive CTE. Callers that need only one of them pass the matching flag. MySQL
rejects a recursive CTE nested inside another, so both results are produced
here, in one WITH clause, rather than by composing the two annotations.

The related rows are loaded afterwards by ``attach_inherited_fields``.
"""

from django.db.models import F, QuerySet
from django_cte import CTE, with_cte

from traceability.models.action import Action
from traceability.services.inherited_fields import inherited_annotation, inherited_climb, inherited_start
from traceability.services.total_emissions import emission_annotation, emission_climb, emission_start


def _plain_actions():
    # Recursive CTE: no Meta.ordering, no status subqueries (MySQL rejects both).
    return Action.unannotated.all().order_by()


def _contributions(*, emissions: bool, inherited_fields: bool):
    # Table of climbers. Each entry describes how its value walks up the tree.
    parts = []
    if emissions:
        parts.append((emission_start, emission_climb, emission_annotation))
    if inherited_fields:
        parts.append((inherited_start, inherited_climb, inherited_annotation))
    return parts


def _chain_cte(queryset: QuerySet[Action], *, emissions: bool, inherited_fields: bool) -> CTE:
    actions = _plain_actions()
    listed = actions.filter(pk__in=queryset)
    parts = _contributions(emissions=emissions, inherited_fields=inherited_fields)

    def columns(cte=None):
        # Generic step: set the attributes the recursive query needs.
        merged = {}
        for start, climb, _annotate in parts:
            merged.update(start() if cte is None else climb(cte))
        return merged

    def walk(cte):
        # Link each action to its parent and carry the attributes one step up.
        start_from_listed = listed.values(
            origin_id=F("id"),
            next_parent_id=F("parent_id"),
            **columns(),
        )
        climb_to_parent = cte.join(actions, id=cte.col.next_parent_id).values(
            origin_id=cte.col.origin_id,
            next_parent_id=F("parent_id"),
            **columns(cte),
        )
        return start_from_listed.union(climb_to_parent, all=True)

    return CTE.recursive(walk, name="parent_chain")


def annotate_parent_chain(
    queryset: QuerySet[Action],
    *,
    emissions: bool = True,
    inherited_fields: bool = True,
) -> QuerySet[Action]:
    """Annotate `total_emissions` and/or the inherited material ids from the parent chain."""
    if not emissions and not inherited_fields:
        return queryset

    cte = _chain_cte(queryset, emissions=emissions, inherited_fields=inherited_fields)
    # Parent pointer, plus what each climber attaches to the action.
    annotations = {"_next_parent_id": cte.col.next_parent_id}
    for _start, _climb, annotate in _contributions(emissions=emissions, inherited_fields=inherited_fields):
        annotations.update(annotate(cte))

    # Keep the row that reached the root and put it back on the action.
    at_root = cte.join(queryset, id=cte.col.origin_id).annotate(**annotations).filter(_next_parent_id__isnull=True)
    return with_cte(cte, select=at_root.order_by("id"))

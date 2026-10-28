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
    # Mysql refuse les sous-requetes et order by dans une requete récursive
    # Ici "queryset" a les sous-requetes status, created_at, updated_at etc... + l'order by par défaut définit sur la table
    # Donc on réinitialise l'order by et on ne prend que les ids
    listed = actions.filter(pk__in=queryset.order_by().values("pk"))
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

    # Keep the caller's sort. Fall back to id when the queryset has none.
    ordering = queryset.query.order_by or ("id",)
    at_root = cte.join(queryset, id=cte.col.origin_id).annotate(**annotations).filter(_next_parent_id__isnull=True)
    return with_cte(cte, select=at_root.order_by(*ordering))


def _origin_ids(queryset: QuerySet[Action], material_ids: list[int] | None = None):
    """Walk to the root and return ``(action id, origin material id)``.

    The recursive member carries material ids only. The action row, its status
    subqueries and the GES sums stay out of this statement. ``material_ids``
    restricts the rows that come back; the walk itself still sees every action.
    """
    cte = _chain_cte(queryset, emissions=False, inherited_fields=True)
    # Meta.ordering is `id`, which is not a column of this CTE.
    at_root = cte.queryset().filter(next_parent_id__isnull=True).order_by()
    if material_ids is not None:
        at_root = at_root.filter(origin_material_id__in=material_ids)
    return with_cte(cte, select=at_root).values_list("origin_id", "origin_material_id")


def filter_by_origin_material(queryset: QuerySet[Action], material_ids: list[int]) -> QuerySet[Action]:
    """Keep actions whose origin material is one of ``material_ids``.

    The walk runs once. The returned queryset is the caller's, restricted to
    the matching ids, so the page count does not walk again.
    """
    if not material_ids:
        return queryset.none()

    matching_ids = [action_id for action_id, _origin_material_id in _origin_ids(queryset, material_ids)]
    return queryset.filter(pk__in=matching_ids)


def origin_material_ids(queryset: QuerySet[Action]) -> list[int]:
    """Distinct origin material ids for a queryset. One walk, no action join."""
    return list({origin_material_id for _action_id, origin_material_id in _origin_ids(queryset) if origin_material_id})

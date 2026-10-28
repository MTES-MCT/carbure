"""Climb each action's parent chain once, up to the root.

The columns it carries are declared in ``services/climbers.py``. Callers pass
the climber names they need. MySQL rejects a recursive CTE nested inside
another, so every requested column is produced here, in one WITH clause.

The related rows are loaded afterwards by ``attach_inherited_fields``.
"""

from collections.abc import Iterable

from django.db.models import F, QuerySet
from django_cte import CTE, with_cte

from traceability.models.action import Action
from traceability.services.climbers import CLIMBERS, PAGE_CLIMBERS
from traceability.services.inherited_fields import ROOT_COLUMNS


def _plain_actions():
    # Recursive CTE: no Meta.ordering, no status subqueries (MySQL rejects both).
    return Action.unannotated.all().order_by()


def _names(climbers: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(climbers))


def _chain_cte(queryset: QuerySet[Action], climbers: Iterable[str]) -> CTE:
    actions = _plain_actions()
    # Mysql refuse les sous-requetes et order by dans une requete récursive
    # Ici "queryset" a les sous-requetes status, created_at, updated_at etc... + l'order by par défaut définit sur la table
    # Donc on réinitialise l'order by et on ne prend que les ids
    listed = actions.filter(pk__in=queryset.order_by().values("pk"))
    parts = [CLIMBERS[name] for name in _names(climbers)]

    def columns(cte=None):
        # UNION lines up columns by position. start and climb must share keys, in the same order.
        merged = {}
        for climber in parts:
            started = climber.start()
            step = started if cte is None else climber.climb(cte)
            if list(step) != list(started):
                raise ValueError(f"climb columns {list(step)} must match start columns {list(started)}")
            shared = set(merged).intersection(step)
            if shared:
                raise ValueError(f"climbers share columns: {sorted(shared)}")
            merged.update(step)
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


def _at_root(queryset: QuerySet[Action], climbers: Iterable[str]):
    cte = _chain_cte(queryset, climbers)
    # Meta.ordering is `id`, which is not a column of this CTE.
    rows = cte.queryset().filter(next_parent_id__isnull=True).order_by()
    return cte, rows


def annotate_parent_chain(queryset: QuerySet[Action], *, climbers: Iterable[str] = PAGE_CLIMBERS) -> QuerySet[Action]:
    """Annotate the actions with the columns of the named climbers."""
    names = _names(climbers)
    if not names:
        return queryset

    cte = _chain_cte(queryset, names)
    annotations = {"_next_parent_id": cte.col.next_parent_id}
    for name in names:
        annotate = CLIMBERS[name].annotate
        if annotate is not None:
            annotations.update(annotate(cte))

    # Keep the caller's sort. Fall back to id when the queryset has none.
    ordering = queryset.query.order_by or ("id",)
    at_root = cte.join(queryset, id=cte.col.origin_id).annotate(**annotations).filter(_next_parent_id__isnull=True)
    return with_cte(cte, select=at_root.order_by(*ordering))


def chain_column(queryset: QuerySet[Action], column: str, climbers: Iterable[str]):
    """Walk to the root and return ``(action id, column)``. No emissions, no action row."""
    cte, rows = _at_root(queryset, climbers)
    return with_cte(cte, select=rows).values_list("origin_id", column)


def _matching_roots(columns: dict[str, list]) -> list[int] | None:
    """Primary keys of the roots matching every root column in ``columns``.

    ``None`` when no root column is requested.
    """
    selected = {ROOT_COLUMNS[column]: values for column, values in columns.items() if column in ROOT_COLUMNS}
    if not selected:
        return None
    roots = _plain_actions().filter(parent__isnull=True)
    for field, values in selected.items():
        roots = roots.filter(**{f"{field}__in": values})
    return list(roots.values_list("pk", flat=True))


# Voir commentaire ci-dessous
def _descendant_ids(root_ids: list[int]) -> list[int]:
    """The roots and every action below them."""
    actions = _plain_actions()
    listed = actions.filter(pk__in=root_ids)

    def walk(cte):
        start = listed.values(action_id=F("id"))
        children = cte.join(actions, parent_id=cte.col.action_id).values(action_id=F("id"))
        return start.union(children, all=True)

    cte = CTE.recursive(walk, name="descendants")
    # Meta.ordering is `id`, which is not a column of this CTE.
    rows = cte.queryset().order_by()
    return list(with_cte(cte, select=rows).values_list("action_id", flat=True))


def filter_by_chain(queryset: QuerySet[Action], columns: dict[str, list], climbers: Iterable[str]) -> QuerySet[Action]:
    """Keep actions whose chain columns match every entry of ``columns``.

    The returned queryset is the caller's, restricted to the matching ids.
    """
    if not columns:
        return queryset

    # producer et root_pos (ROOT_COLUMNS) sont des valeurs stockées sur l'action racine.
    # Une requête normale trouve ces racines. On ne descend vers leurs enfants que si elles
    # sont moins nombreuses que la liste déjà filtrée (type, année, périmètre) : un pos_id
    # vise souvent une seule chaîne, la descente ne parcourt qu'elle.
    # Si le filtre vise presque toutes les racines (producer = le titulaire de toute la
    # forêt), descendre recalculerait chaque action. On remonte alors depuis la liste, qui
    # est déjà plus petite. origin_material et nearest_site remontent de la même façon.
    root_ids = _matching_roots(columns)
    if root_ids is not None:
        if not root_ids:
            return queryset.none()
        if len(root_ids) < queryset.count():
            queryset = queryset.filter(pk__in=_descendant_ids(root_ids))
            columns = {column: values for column, values in columns.items() if column not in ROOT_COLUMNS}
    if not columns:
        return queryset

    cte, rows = _at_root(queryset, climbers)
    for column, values in columns.items():
        rows = rows.filter(**{f"{column}__in": values})
    # Materialize once. A subquery would rerun the walk for the page count and the page.
    matching_ids = list(with_cte(cte, select=rows).values_list("origin_id", flat=True))
    return queryset.filter(pk__in=matching_ids)

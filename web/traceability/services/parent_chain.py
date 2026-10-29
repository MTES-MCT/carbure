"""Climb each action's parent chain once, up to the root.

Callers pass group names from ``services/column_groups.py``. MySQL rejects a
recursive CTE nested inside another, so every requested column is produced
here, in one WITH clause.

Walkthrough: ``traceability/docs/parent_chain.md``.
"""

from collections.abc import Iterable

from django.db.models import F, QuerySet
from django_cte import CTE, with_cte

from traceability.models.action import Action
from traceability.services.column_groups import COLUMN_GROUPS, PAGE_COLUMN_GROUPS
from traceability.services.inherited_fields import ROOT_COLUMNS


def _plain_actions():
    # Recursive CTE: no Meta.ordering, no status subqueries (MySQL rejects both).
    return Action.unannotated.all().order_by()


def _names(groups: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(groups))


def _chain_cte(queryset: QuerySet[Action], groups: Iterable[str]) -> CTE:
    actions = _plain_actions()
    # MySQL rejects ORDER BY and a status subquery inside a recursive CTE.
    # The caller queryset may carry both when the list filters by status.
    # The walk stays on plain actions and receives only ids.
    listed = actions.filter(pk__in=queryset.order_by().values("pk"))
    parts = [COLUMN_GROUPS[name] for name in _names(groups)]

    def columns(cte=None):
        # UNION lines up columns by position. start and climb must share keys, in the same order.
        merged = {}
        for group in parts:
            started = group.start()
            step = started if cte is None else group.climb(cte)
            if list(step) != list(started):
                raise ValueError(f"climb columns {list(step)} must match start columns {list(started)}")
            shared = set(merged).intersection(step)
            if shared:
                raise ValueError(f"column groups share columns: {sorted(shared)}")
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


def _at_root(queryset: QuerySet[Action], groups: Iterable[str]):
    cte = _chain_cte(queryset, groups)
    # Meta.ordering is `id`, which is not a column of this CTE.
    rows = cte.queryset().filter(next_parent_id__isnull=True).order_by()
    return cte, rows


def annotate_parent_chain(queryset: QuerySet[Action], *, groups: Iterable[str] = PAGE_COLUMN_GROUPS) -> QuerySet[Action]:
    """Annotate the actions with the columns of the named groups."""
    names = _names(groups)
    if not names:
        return queryset

    cte = _chain_cte(queryset, names)
    annotations = {"_next_parent_id": cte.col.next_parent_id}
    for name in names:
        annotate = COLUMN_GROUPS[name].annotate
        if annotate is not None:
            annotations.update(annotate(cte))

    # Keep the caller's sort. Fall back to id when the queryset has none.
    ordering = queryset.query.order_by or ("id",)
    at_root = cte.join(queryset, id=cte.col.origin_id).annotate(**annotations).filter(_next_parent_id__isnull=True)
    return with_cte(cte, select=at_root.order_by(*ordering))


def chain_column(queryset: QuerySet[Action], column: str, groups: Iterable[str]):
    """Walk to the root and return ``(action id, column)``. No emissions, no action row."""
    cte, rows = _at_root(queryset, groups)
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


def load_action_tree(action_id: int) -> list[dict]:
    """Every node of the action's tree: the root and all of its descendants.

    Two short walks, then one query for id, type, holder and site.
    """
    root_id = _root_id(action_id)
    ids = _descendant_ids([root_id]) or [action_id]
    rows = (
        _plain_actions()
        .filter(pk__in=ids)
        .order_by("id")
        .values("id", "parent_id", "type", "holder_id", "holder__name", "site_id", "site__name")
    )
    return [
        {
            "id": row["id"],
            "parent_id": row["parent_id"],
            "type": row["type"],
            "holder": {"id": row["holder_id"], "name": row["holder__name"]},
            "site": {"id": row["site_id"], "name": row["site__name"]} if row["site_id"] else None,
        }
        for row in rows
    ]


def _root_id(action_id: int) -> int:
    actions = _plain_actions()
    listed = actions.filter(pk=action_id)

    def walk(cte):
        start = listed.values(node_id=F("id"), next_parent_id=F("parent_id"))
        climb = cte.join(actions, id=cte.col.next_parent_id).values(node_id=F("id"), next_parent_id=F("parent_id"))
        return start.union(climb, all=True)

    cte = CTE.recursive(walk, name="ancestors")
    # `.first()` orders by the model pk (`id`), which this CTE does not have.
    rows = cte.queryset().filter(next_parent_id__isnull=True).order_by("node_id")
    root = with_cte(cte, select=rows).values_list("node_id", flat=True).first()
    return root or action_id


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


def filter_by_chain(queryset: QuerySet[Action], columns: dict[str, list], groups: Iterable[str]) -> QuerySet[Action]:
    """Keep actions whose chain columns match every entry of ``columns``.

    The returned queryset is the caller's, restricted to the matching ids.
    """
    if not columns:
        return queryset

    # Une colonne de ROOT_COLUMNS est stockée sur l'action racine. Une requête normale
    # trouve ces racines. On ne descend vers leurs enfants que si elles sont moins
    # nombreuses que la liste déjà filtrée : un pos_id vise souvent une seule chaîne.
    # Si le filtre vise presque toutes les racines, descendre recalculerait chaque action.
    # On remonte alors depuis la liste, qui est déjà plus petite.
    root_ids = _matching_roots(columns)
    if root_ids is not None:
        if not root_ids:
            return queryset.none()
        if len(root_ids) < queryset.count():
            queryset = queryset.filter(pk__in=_descendant_ids(root_ids))
            columns = {column: values for column, values in columns.items() if column not in ROOT_COLUMNS}
    if not columns:
        return queryset

    cte, rows = _at_root(queryset, groups)
    for column, values in columns.items():
        rows = rows.filter(**{f"{column}__in": values})
    # Une sous-requête relancerait le parcours pour le COUNT de la page, puis pour la page.
    matching_ids = list(with_cte(cte, select=rows).values_list("origin_id", flat=True))
    return queryset.filter(pk__in=matching_ids)

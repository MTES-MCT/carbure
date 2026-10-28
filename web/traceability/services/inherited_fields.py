"""Values the front receives from the parent-chain walk.

The walk lives in ``services/parent_chain.py`` and always reaches the root.
This climber carries the raw ids. ``attach_inherited_fields`` loads the rows
and sets ``action.inherited_fields``.

``previous_material`` is the nearest declared material above the action.
The climb keeps the first non-empty value. The action's own material is ignored.

``origin_material`` is the first declared material from the root. A parent
replaces the value so far. The action's own material is kept when nothing
above declares one.

``nearest_site`` is the first site above the action, same keep-first rule.
The action's own site is ignored.

``producer`` and ``root_pos`` are the holder and the ``pos_id`` of the root.
Each step replaces them with the parent's, so the last row is the root.
``ROOT_COLUMNS`` maps those columns to the field stored on the root action.
A filter on one of them selects the roots directly, then walks down to their
children. A new root filter adds one entry there.

A new value returned to the front is declared in ``inherited_start``,
``inherited_climb``, ``inherited_annotation``, ``attach_inherited_fields``,
and on ``ActionInheritedFieldsSerializer``.

Walkthrough: ``traceability/docs/inherited_fields.md``.
"""

from django.db.models import BigIntegerField, F, QuerySet, Value
from django.db.models.functions import Cast, Coalesce

from core.models import Entity
from traceability.models.action import Action
from traceability.models.material import Material
from transactions.models import Site

_ID = BigIntegerField()

# Filter columns that are copied from the root action. The value is the field on that action.
ROOT_COLUMNS = {
    "root_holder_id": "holder_id",
    "root_pos_id": "pos_id",
}


def _empty_id():
    # A bare NULL makes MySQL infer a zero-width column, then the parent id does not fit.
    return Cast(Value(None), output_field=_ID)


def inherited_start() -> dict:
    return {
        "previous_material_id": _empty_id(),
        "origin_material_id": F("material_id"),
        "nearest_site_id": _empty_id(),
        "root_holder_id": F("holder_id"),
        "root_pos_id": F("pos_id"),
    }


def inherited_climb(cte) -> dict:
    parent_material_id = F("material_id")
    return {
        "previous_material_id": Coalesce(cte.col.previous_material_id, parent_material_id, output_field=_ID),
        "origin_material_id": Coalesce(parent_material_id, cte.col.origin_material_id),
        "nearest_site_id": Coalesce(cte.col.nearest_site_id, F("site_id"), output_field=_ID),
        "root_holder_id": F("holder_id"),
        "root_pos_id": F("pos_id"),
    }


def inherited_annotation(cte) -> dict:
    return {
        "previous_material_id": cte.col.previous_material_id,
        "origin_material_id": cte.col.origin_material_id,
        "nearest_site_id": cte.col.nearest_site_id,
        "root_holder_id": cte.col.root_holder_id,
        "root_pos_id": cte.col.root_pos_id,
    }


def attach_inherited_fields(actions: list[Action]) -> list[Action]:
    """Load the resolved rows and set ``inherited_fields`` on each action."""
    material_ids = {
        material_id
        for action in actions
        for material_id in (action.previous_material_id, action.origin_material_id)
        if material_id
    }

    site_ids = {action.nearest_site_id for action in actions if action.nearest_site_id}
    holder_ids = {action.root_holder_id for action in actions}
    materials = Material.objects.in_bulk(material_ids)
    sites = Site.objects.in_bulk(site_ids)
    holders = Entity.objects.in_bulk(holder_ids)
    for action in actions:
        action.inherited_fields = {
            "previous_material": materials.get(action.previous_material_id),
            "origin_material": materials.get(action.origin_material_id),
            "nearest_site": sites.get(action.nearest_site_id),
            "producer": holders.get(action.root_holder_id),
            "root_pos": action.root_pos_id,
        }
    return actions


def annotate_inherited_fields(queryset: QuerySet[Action]) -> QuerySet[Action]:
    from traceability.services.parent_chain import annotate_parent_chain

    return annotate_parent_chain(queryset, climbers=("inherited_fields",))

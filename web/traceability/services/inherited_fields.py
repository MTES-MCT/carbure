"""Inherited-field columns carried by the shared parent-chain CTE.

The recursive walk itself lives in ``services/parent_chain.py``. It always
reaches the root (the GES sum needs that). The walk carries only material ids.
``attach_inherited_fields`` loads the rows afterwards.

``previous_material_id`` is the nearest declared material above the action.
The climb keeps the first non-empty value, so a further ancestor cannot
overwrite it. The action's own material is ignored.

``origin_material_id`` is the first declared material from the root. The climb
lets a parent's material replace the one found so far, so the value closest to
the root wins. The action's own material is kept when nothing above declares one.

A new field is declared in ``inherited_start``, ``inherited_climb``,
``inherited_annotation``, ``attach_inherited_fields``, and on
``ActionInheritedFieldsSerializer``.

Walkthrough: ``traceability/docs/inherited_fields.md``.
"""

from django.db.models import BigIntegerField, F, QuerySet, Value
from django.db.models.functions import Cast, Coalesce

from traceability.models.action import Action
from traceability.models.material import Material

_MATERIAL_ID = BigIntegerField()


def _empty_material_id():
    # A bare NULL makes MySQL infer a zero-width column, then the parent id does not fit.
    return Cast(Value(None), output_field=_MATERIAL_ID)


def inherited_start() -> dict:
    return {
        "previous_material_id": _empty_material_id(),
        "origin_material_id": F("material_id"),
    }


def inherited_climb(cte) -> dict:
    parent_material_id = F("material_id")
    return {
        "previous_material_id": Coalesce(cte.col.previous_material_id, parent_material_id, output_field=_MATERIAL_ID),
        "origin_material_id": Coalesce(parent_material_id, cte.col.origin_material_id),
    }


def inherited_annotation(cte) -> dict:
    return {
        "previous_material_id": cte.col.previous_material_id,
        "origin_material_id": cte.col.origin_material_id,
    }


def attach_inherited_fields(actions: list[Action]) -> list[Action]:
    """Load the resolved rows and set ``inherited_fields`` on each action."""
    material_ids = {
        material_id
        for action in actions
        for material_id in (action.previous_material_id, action.origin_material_id)
        if material_id
    }

    materials = Material.objects.in_bulk(material_ids)
    for action in actions:
        action.inherited_fields = {
            "previous_material": materials.get(action.previous_material_id),
            "origin_material": materials.get(action.origin_material_id),
        }
    return actions


def annotate_inherited_fields(queryset: QuerySet[Action]) -> QuerySet[Action]:
    from traceability.services.parent_chain import annotate_parent_chain

    return annotate_parent_chain(queryset, emissions=False)

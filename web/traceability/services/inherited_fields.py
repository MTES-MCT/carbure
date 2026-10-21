"""Inherited-field columns carried by the shared parent-chain CTE.

The recursive walk itself lives in ``services/parent_chain.py``. It always
reaches the root (the GES sum needs that). The first non-empty value is kept
with COALESCE, so a later ancestor cannot overwrite it. The walk carries only
ids. ``attach_inherited_fields`` loads the rows afterwards.

A new field is declared in ``inherited_start``, ``inherited_climb``,
``inherited_annotation``, ``attach_inherited_fields``, and on
``ActionInheritedFieldsSerializer``.

Walkthrough: ``traceability/docs/inherited_fields.md``.
"""

from django.db.models import F, QuerySet
from django.db.models.functions import Coalesce

from traceability.models.action import Action
from traceability.models.material import Material


def inherited_start() -> dict:
    return {"found_material_id": F("material_id")}


def inherited_climb(cte) -> dict:
    return {"found_material_id": Coalesce(cte.col.found_material_id, F("material_id"))}


def inherited_annotation(cte) -> dict:
    return {"found_material_id": cte.col.found_material_id}


def attach_inherited_fields(actions: list[Action]) -> list[Action]:
    """Load the resolved rows and set ``inherited_fields`` on each action."""
    materials = Material.objects.in_bulk({action.found_material_id for action in actions if action.found_material_id})
    for action in actions:
        action.inherited_fields = {
            "material": materials.get(action.found_material_id),
        }
    return actions


def annotate_inherited_fields(queryset: QuerySet[Action]) -> QuerySet[Action]:
    from traceability.services.parent_chain import annotate_parent_chain

    return annotate_parent_chain(queryset, emissions=False)

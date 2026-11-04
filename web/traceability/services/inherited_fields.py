"""Raw ids carried by the ``inherited_fields`` column group.

``attach_inherited_fields`` loads the rows and sets ``action.inherited_fields``.
Field rules: ``traceability/docs/inherited_fields.md``.
The walk and ``ROOT_COLUMNS``: ``traceability/docs/parent_chain.md``.
"""

from django.db.models import BigIntegerField, F, QuerySet, Value
from django.db.models.functions import Cast, Coalesce

from traceability.models.action import Action
from traceability.models.material import Material

_ID = BigIntegerField()

# Vide : aucun filtre ne lit encore une valeur stockée sur la racine.
# Tout champ qui vient de la racine se déclare ici.
# La clé est la colonne portée par le parcours, la valeur est le champ sur l'action racine.
ROOT_COLUMNS = {}


def _empty_id():
    # A bare NULL makes MySQL infer a zero-width column, then the parent id does not fit.
    return Cast(Value(None), output_field=_ID)


def inherited_start() -> dict:
    return {
        "previous_material_id": _empty_id(),
        "origin_material_id": F("material_id"),
    }


def inherited_climb(cte) -> dict:
    parent_material_id = F("material_id")
    return {
        "previous_material_id": Coalesce(cte.col.previous_material_id, parent_material_id, output_field=_ID),
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

    return annotate_parent_chain(queryset, groups=("inherited_fields",))

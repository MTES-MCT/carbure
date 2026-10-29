"""Raw ids carried by the ``inherited_fields`` column group.

``attach_inherited_fields`` loads the rows and sets ``action.inherited_fields``.
Field rules: ``traceability/docs/inherited_fields.md``.
The walk and ``ROOT_COLUMNS``: ``traceability/docs/parent_chain.md``.
"""

from django.db.models import BigIntegerField, F, QuerySet, Value
from django.db.models.functions import Cast, Coalesce

from core.models import Entity
from traceability.models.action import Action
from traceability.models.material import Material
from transactions.models import Site

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

    return annotate_parent_chain(queryset, groups=("inherited_fields",))

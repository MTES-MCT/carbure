from typing import Any, Callable

from biomethane.services.declaration_export import _get_display_value
from core.excel import Column


def _display(field: str) -> Callable[[Any], str]:
    def getter(row: Any) -> str:
        value = _get_display_value(row, field)
        return "" if value is None else value

    return getter


def _production_unit_display(field: str) -> Callable[[Any], str]:
    def getter(row: Any) -> str:
        value = _get_display_value(row.supply_plan.producer.biomethane_production_unit, field)
        return "" if value is None else value

    return getter


DREAL_PREFIX_COLUMNS: list[Column] = [
    {"label": "Producteur", "value": "supply_plan.producer.name"},
    {"label": "Type d'installation", "value": _production_unit_display("unit_type")},
    {"label": "Département", "value": "supply_plan.producer.biomethane_production_unit.department.code_dept"},
]

BASE_COLUMNS: list[Column] = [
    {"label": "Provenance", "value": _display("source")},
    {"label": "Intrant", "value": "feedstock.name"},
    {"label": "Catégorie", "value": "feedstock.classification.category"},
    {"label": "Sous-catégorie", "value": "feedstock.classification.subcategory"},
    {"label": "Unité", "value": _display("material_unit")},
    {"label": "Ratio de matière sèche (%)", "value": "dry_matter_ratio_percent"},
    {"label": "Volume (t)", "value": "volume"},
    {"label": "Département d'origine", "value": "origin_department"},
    {"label": "Distance moyenne pondérée (km)", "value": "average_weighted_distance_km"},
    {"label": "Distance maximale (km)", "value": "maximum_distance_km"},
    {"label": "Pays d'origine", "value": "origin_country.name"},
    {"label": "Type de CIVE", "value": _display("type_cive")},
    {"label": "Précisez la culture", "value": "culture_details"},
    {"label": "Type de collecte", "value": _display("collection_type")},
    {"label": "Année", "value": "supply_plan.year"},
]


def build_columns(*, dreal: bool) -> list[Column]:
    if dreal:
        return DREAL_PREFIX_COLUMNS + BASE_COLUMNS
    return BASE_COLUMNS

from core.excel import Column

DREAL_PREFIX_COLUMNS: list[Column] = [
    {"label": "Producteur", "value": "producer.name"},
    {"label": "Type d'installation", "value": "production_unit.unit_type"},
    {"label": "Département", "value": "production_unit.department"},
]

BASE_COLUMNS: list[Column] = [
    {"label": "Provenance", "value": "source"},
    {"label": "Intrant", "value": "feedstock.name"},
    {"label": "Catégorie", "value": "feedstock.classification.category"},
    {"label": "Sous-catégorie", "value": "feedstock.classification.subcategory"},
    {"label": "Unité", "value": "material_unit"},
    {"label": "Ratio de matière sèche (%)", "value": "dry_matter_ratio_percent"},
    {"label": "Volume (t)", "value": "volume"},
    {"label": "Département d'origine", "value": "origin_department"},
    {"label": "Distance moyenne pondérée (km)", "value": "average_weighted_distance_km"},
    {"label": "Distance maximale (km)", "value": "maximum_distance_km"},
    {"label": "Pays d'origine", "value": "origin_country"},
    {"label": "Type de CIVE", "value": "type_cive"},
    {"label": "Précisez la culture", "value": "culture_details"},
    {"label": "Type de collecte", "value": "collection_type"},
    {"label": "Année", "value": "year"},
]


def build_columns(*, dreal: bool) -> list[Column]:
    if dreal:
        return DREAL_PREFIX_COLUMNS + BASE_COLUMNS
    return BASE_COLUMNS

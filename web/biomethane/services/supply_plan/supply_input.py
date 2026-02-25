"""
Business rules for supply input fields that depend on the selected feedstock (MatierePremiere).

Each rule is a dict with:
- field: name of the BiomethaneSupplyInput field that is conditionally required.
- condition: callable(feedstock, data) -> bool. Receives the feedstock (MatierePremiere) and the
  validated_data dict. Returns True if the rule applies (the field is then required).
- error_message: message shown when the rule applies but the field is empty.
"""

# Code of feedstock for which volume, material_unit and dry_matter_ratio_percent are optional.
from biomethane.models.biomethane_supply_input import BiomethaneSupplyInput

BIOGAZ_CAPTE_ISDND_FEEDSTOCK_CODE = "BIOGAZ-CAPTE-DUNE-ISDND"

# Codes of feedstocks that require the "collection_type" field (used in Excel template for rules text).
COLLECTION_TYPE_REQUIRED_FEEDSTOCK_CODES = frozenset(
    {
        "HUILES-ALIMENTAIRES-USAGEES-DORIGINE-ANIMALE",
        "HUILES-ALIMENTAIRES-USAGEES-DORIGINE-VEGETALE",
        "HUILES-ALIMENTAIRES-USAGEES-DORIGINE-NON-SPECIFIEE",
        "GRAISSES-DE-BACS-A-GRAISSE-DE-RESTAURATION",
        "AUTRE-DECHETS-GRAISSEUX",
        "HUILES-ET-MATIERES-GRASSES-AVEC-PRODUITS-ANIMAUX-CAT-1",
        "HUILES-ET-MATIERES-GRASSES-AVEC-PRODUITS-ANIMAUX-CAT-2",
        "HUILES-ET-MATIERES-GRASSES-AVEC-PRODUITS-ANIMAUX-CAT-3",
    }
)


def _feedstock_is_not_biogaz_capte_isdnd(feedstock, data):
    """True if feedstock is set and its code is not BIOGAZ-CAPTE-DUNE-ISDND (signature for rule condition)."""
    return getattr(feedstock, "code", None) != BIOGAZ_CAPTE_ISDND_FEEDSTOCK_CODE


# When condition(feedstock, data) is True, the field is required; otherwise it is set to None.
FEEDSTOCK_FIELD_RULES = (
    {
        "field": "type_cive",
        "condition": lambda feedstock, data: (
            getattr(getattr(feedstock, "classification", None), "category", None)
            == "Biomasse agricole - Cultures intermédiaires"
        ),
        "error_message": "Le champ type de CIVE est requis pour cette matière première.",
    },
    {
        "field": "culture_details",
        "condition": lambda feedstock, data: getattr(feedstock, "code", None)
        in (
            "AUTRES-CULTURES",
            "AUTRES-CULTURES-CIVE",
        ),
        "error_message": "Le champ précisez la culture est requis pour cette matière première.",
    },
    {
        "field": "collection_type",
        "condition": lambda feedstock, data: getattr(feedstock, "code", None) in COLLECTION_TYPE_REQUIRED_FEEDSTOCK_CODES,
        "error_message": "Le champ type de collecte est requis pour cette matière première.",
    },
    {
        "field": "volume",
        "condition": _feedstock_is_not_biogaz_capte_isdnd,
        "error_message": "Le champ volume est requis.",
    },
    {
        "field": "material_unit",
        "condition": _feedstock_is_not_biogaz_capte_isdnd,
        "error_message": "Le champ unité matière est requis.",
    },
    {
        "field": "dry_matter_ratio_percent",
        "condition": lambda feedstock, data: _feedstock_is_not_biogaz_capte_isdnd(feedstock, data)
        and data.get("material_unit", None) == BiomethaneSupplyInput.DRY,
        "error_message": "Le champ ratio de matière sèche est requis.",
    },
)


def _rule_applies(rule, feedstock, data):
    """True if the rule applies (condition(feedstock, data) returns True)."""
    return bool(rule["condition"](feedstock, data))


def apply_feedstock_field_rules(validated_data):
    """
    Apply feedstock-dependent business rules: clear or require fields, return validation errors.

    Updates validated_data in place (sets conditional fields to None when the rule does not apply).
    Returns a dict of field -> error_message for fields that are required but empty; the caller
    should raise ValidationError(errors) when the dict is non-empty.

    validated_data must contain "feedstock" (MatierePremiere or None) and the rule field names.
    Each rule defines condition(feedstock, data) to decide whether it applies.
    """
    errors = {}
    feedstock = validated_data.get("feedstock")

    if not feedstock:
        for rule in FEEDSTOCK_FIELD_RULES:
            validated_data[rule["field"]] = None
        return errors

    for rule in FEEDSTOCK_FIELD_RULES:
        field = rule["field"]
        if _rule_applies(rule, feedstock, validated_data):
            if not validated_data.get(field):
                errors[field] = rule["error_message"]
        else:
            validated_data[field] = None

    return errors

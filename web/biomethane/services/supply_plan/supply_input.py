"""
Business rules for supply input fields that depend on the selected feedstock (MatierePremiere).

Each rule is a dict with:
- field: name of the BiomethaneSupplyInput field that is conditionally required.
- condition: callable(feedstock, data) -> bool. Receives the feedstock (MatierePremiere) and the
  validated_data dict. Returns True if the rule applies (the field is then required).
- error_message: message shown when the rule applies but the field is empty.
"""

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
        "condition": lambda feedstock, data: getattr(feedstock, "code", None)
        in (
            "HUILES-ALIMENTAIRES-USAGEES-DORIGINE-ANIMALE",
            "HUILES-ALIMENTAIRES-USAGEES-DORIGINE-VEGETALE",
            "HUILES-ALIMENTAIRES-USAGEES-DORIGINE-NON-SPECIFIEE",
            "GRAISSES-DE-BACS-A-GRAISSE-DE-RESTAURATION",
            "AUTRE-DECHETS-GRAISSEUX",
            "HUILES-ET-MATIERES-GRASSES-AVEC-PRODUITS-ANIMAUX-CAT-1",
            "HUILES-ET-MATIERES-GRASSES-AVEC-PRODUITS-ANIMAUX-CAT-2",
            "HUILES-ET-MATIERES-GRASSES-AVEC-PRODUITS-ANIMAUX-CAT-3",
        ),
        "error_message": "Le champ type de collecte est requis pour cette matière première.",
    },
    {
        "field": "volume",
        "condition": lambda feedstock, data: getattr(feedstock, "code", None) != "BIOGAZ-CAPTE-DUNE-ISDND",
        "error_message": "Le champ volume est requis.",
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

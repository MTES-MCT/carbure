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
        "error_message": "CIVE type is required for this feedstock.",
    },
    {
        "field": "culture_details",
        "condition": lambda feedstock, data: getattr(feedstock, "code", None)
        in (
            "AUTRES_CULTURES",
            "AUTRES_CULTURES_CIVE",
        ),
        "error_message": "Please specify the crop for this feedstock.",
    },
    {
        "field": "collection_type",
        "condition": lambda feedstock, data: getattr(feedstock, "name", None)
        in (
            "Huiles alimentaires usagées d'origine animale",
            "Huiles alimentaires usagées d'origine végétale",
            "Huiles alimentaires usagées d'origine non-spécifiée",
            "Graisses de bacs à graisse de restauration",
            "Autre déchets graisseux",
            "Huiles et matières grasses (avec produits animaux) (Cat 1)",
            "Huiles et matières grasses (avec produits animaux) (Cat 2)",
            "Huiles et matières grasses (avec produits animaux) (Cat 3)",
        ),
        "error_message": "Collection type is required for this feedstock.",
    },
    {
        "field": "volume",
        "condition": lambda feedstock, data: getattr(feedstock, "name", None) != "X",
        "error_message": "Volume is required for this feedstock.",
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

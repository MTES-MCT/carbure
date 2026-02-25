"""
Business rules for supply input fields that depend on the selected feedstock (MatierePremiere).

A business rule is a dict with:
- field: name of the BiomethaneSupplyInput field that is conditionally required.
- check_type: which attribute of the feedstock to check — "classification_category"
  (feedstock.classification.category), "input_code" (feedstock.code), or "feedstock_name"
  (feedstock.name).
- value: expected value for the condition. If a str, equality is used; if a tuple,
  the check is "value in tuple".
- error_message: validation message shown when the rule applies but the field is empty.
"""

# Rules: when the condition matches, the field is required; otherwise it is cleared to None.
FEEDSTOCK_FIELD_RULES = (
    {
        "field": "type_cive",
        "check_type": "classification_category",
        "value": "Biomasse agricole - Cultures intermédiaires",
        "error_message": "Le type de CIVE est requis pour cet intrant.",
    },
    {
        "field": "culture_details",
        "check_type": "input_code",
        "value": ("AUTRES_CULTURES", "AUTRES_CULTURES_CIVE"),
        "error_message": "Précisez la culture pour cet intrant.",
    },
    {
        "field": "collection_type",
        "check_type": "feedstock_name",
        "value": (
            "Huiles alimentaires usagées d'origine animale",
            "Huiles alimentaires usagées d'origine végétale",
            "Huiles alimentaires usagées d'origine non-spécifiée",
            "Graisses de bacs à graisse de restauration",
            "Autre déchets graisseux",
            "Huiles et matières grasses (avec produits animaux) (Cat 1)",
            "Huiles et matières grasses (avec produits animaux) (Cat 2)",
            "Huiles et matières grasses (avec produits animaux) (Cat 3)",
        ),
        "error_message": "Le type de collecte est requis pour cet intrant.",
    },
)


def _get_feedstock_check_value(feedstock, check_type):
    """Return the value used for the condition from the given feedstock (MatierePremiere)."""
    if check_type == "classification_category":
        return feedstock.classification.category if feedstock.classification else None
    if check_type == "input_code":
        return feedstock.code
    if check_type == "feedstock_name":
        return feedstock.name
    return None


def _feedstock_matches_rule(check_value, rule):
    """Return True if check_value satisfies the rule (equality or membership)."""
    rule_value = rule["value"]
    if isinstance(rule_value, tuple):
        return check_value in rule_value
    return check_value == rule_value


def apply_feedstock_field_rules(validated_data):
    """
    Apply feedstock-dependent business rules: clear or require fields, return validation errors.

    Updates validated_data in place (sets conditional fields to None when the rule does not
    apply). Returns a dict of field -> error_message for fields that are required but empty;
    the caller should raise ValidationError(errors) when the dict is non-empty.

    validated_data must contain "feedstock" (MatierePremiere or None) and the rule field names.
    """
    errors = {}
    feedstock = validated_data.get("feedstock")

    if not feedstock:
        for rule in FEEDSTOCK_FIELD_RULES:
            validated_data[rule["field"]] = None
        return errors

    for rule in FEEDSTOCK_FIELD_RULES:
        field = rule["field"]
        check_value = _get_feedstock_check_value(feedstock, rule["check_type"])
        if _feedstock_matches_rule(check_value, rule):
            if not validated_data.get(field):
                errors[field] = rule["error_message"]
        else:
            validated_data[field] = None

    return errors

"""
Computed attributes for feedstocks.Classification (not persisted).

Rules are evaluated from classification field values (e.g. category label).
Add new rules to CLASSIFICATION_COMPUTED_ATTRIBUTE_RULES and defaults to
DEFAULT_COMPUTED_ATTRIBUTES when introducing new attributes.
"""

from dataclasses import dataclass
from typing import Any

# --- crop_type attribute -------------------------------------------------------


PRIMARY = "PRIMARY"
INTERMEDIATE = "INTERMEDIATE"
CROP_TYPES_CHOICES = [(PRIMARY, PRIMARY), (INTERMEDIATE, INTERMEDIATE)]

CATEGORY_PRIMARY_CROPS = "Biomasse agricole - Cultures pour alimentaiton humaine ou animale (principales)"
CATEGORY_INTERMEDIATE_CROPS = "Biomasse agricole - Cultures intermédiaires"

DEFAULT_COMPUTED_ATTRIBUTES: dict[str, Any] = {
    "crop_type": None,
}


@dataclass(frozen=True)
class ClassificationComputedAttributeRule:
    """
    When classification.<field> equals <equals>, set <attribute> to <value>.
    """

    attribute: str
    value: Any
    field: str
    equals: str


CLASSIFICATION_COMPUTED_ATTRIBUTE_RULES: tuple[ClassificationComputedAttributeRule, ...] = (
    ClassificationComputedAttributeRule(
        attribute="crop_type",
        value=PRIMARY,
        field="category",
        equals=CATEGORY_PRIMARY_CROPS,
    ),
    ClassificationComputedAttributeRule(
        attribute="crop_type",
        value=INTERMEDIATE,
        field="category",
        equals=CATEGORY_INTERMEDIATE_CROPS,
    ),
)


def _rule_matches(classification, rule: ClassificationComputedAttributeRule) -> bool:
    return getattr(classification, rule.field, None) == rule.equals


def resolve_computed_attributes(classification) -> dict[str, Any]:
    """Return all computed attributes for a classification (or defaults if None)."""
    if classification is None:
        return dict(DEFAULT_COMPUTED_ATTRIBUTES)

    attributes = dict(DEFAULT_COMPUTED_ATTRIBUTES)
    for rule in CLASSIFICATION_COMPUTED_ATTRIBUTE_RULES:
        if _rule_matches(classification, rule):
            attributes[rule.attribute] = rule.value
    return attributes


def get_crop_type(classification) -> str | None:
    return resolve_computed_attributes(classification)["crop_type"]

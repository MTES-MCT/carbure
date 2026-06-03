from django.test import TestCase

from feedstocks.classification_computed_attributes import (
    CATEGORY_INTERMEDIATE_CROPS,
    CATEGORY_PRIMARY_CROPS,
    INTERMEDIATE,
    PRIMARY,
    get_crop_type,
)
from feedstocks.models import Classification


class ClassificationComputedAttributesTests(TestCase):
    def test_primary_crop_from_category(self):
        classification = Classification(
            category=CATEGORY_PRIMARY_CROPS,
        )
        self.assertEqual(get_crop_type(classification), PRIMARY)
        self.assertTrue(classification.is_primary_crop)
        self.assertFalse(classification.is_intermediate_crop)

    def test_intermediate_crop_from_category(self):
        classification = Classification(
            category=CATEGORY_INTERMEDIATE_CROPS,
        )
        self.assertEqual(get_crop_type(classification), INTERMEDIATE)
        self.assertTrue(classification.is_intermediate_crop)
        self.assertFalse(classification.is_primary_crop)

    def test_null_when_category_does_not_match(self):
        classification = Classification(category="Autre catégorie")
        self.assertIsNone(get_crop_type(classification))

    def test_null_when_classification_is_none(self):
        self.assertIsNone(get_crop_type(None))

from unittest import TestCase
from unittest.mock import patch

from edelivery.management.commands.export_national_scheme_certificates import carbure_entities


class CarbureEntitiesTest(TestCase):
    def setUp(self):
        self.patched_Entity = patch("edelivery.management.commands.export_national_scheme_certificates.Entity").start()

    def tearDown(self):
        patch.stopall()

    def test_raises_an_error_if_missing_parameter(self):
        with self.assertRaises(ValueError) as context:
            carbure_entities()

        self.assertEqual(
            "Missing parameter: if --all option not set, an entity name should be provided",
            context.exception.args[0],
        )

    def test_fetches_concerned_carbure_entities_through_all_valid_national_scheme_certificates(self):
        query_result = ["entity1", "entity2"]
        patched_all_currently_certified = self.patched_Entity.all_currently_certified_under_national_scheme
        patched_all_currently_certified.return_value = query_result
        patched_all_currently_certified.assert_not_called()

        entities = carbure_entities(fetch_all=True)
        patched_all_currently_certified.assert_called()
        self.assertEqual(query_result, entities)

    def test_raises_an_error_if_no_entity_found(self):
        patched_all_currently_certified = self.patched_Entity.all_currently_certified_under_national_scheme
        patched_all_currently_certified.return_value = []

        with self.assertRaises(RuntimeError) as context:
            carbure_entities(fetch_all=True)

        self.assertEqual(
            "No entity found with currently valid national scheme certificate",
            context.exception.args[0],
        )

    def test_can_fetch_one_specific_carbure_entity_instead(self):
        query_result = ["Some entity"]
        patched_filter = self.patched_Entity.objects.filter
        patched_filter.return_value = query_result
        patched_filter.assert_not_called()

        entity = carbure_entities(entity_name="SOME ENTITY")
        patched_filter.assert_called_with(name="SOME ENTITY")
        self.assertEqual(query_result, entity)

    def test_raises_an_error_if_named_entity_not_found(self):
        patched_filter = self.patched_Entity.objects.filter
        patched_filter.return_value = []

        command = ExportNSCertificates()
        with self.assertRaises(ValueError) as context:
            command.carbure_entities(entity_name="SOME ENTITY")

        self.assertEqual("Value error: Entity 'SOME ENTITY' not found in CarbuRe", context.exception.args[0])

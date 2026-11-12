from unittest import TestCase
from unittest.mock import MagicMock, patch

from edelivery.management.commands.export_national_scheme_certificates import (
    carbure_entities,
    entity_names,
    find_entities_not_in_udb,
)
from entity.factories.entity import EntityFactory


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

        with self.assertRaises(ValueError) as context:
            carbure_entities(entity_name="SOME ENTITY")

        self.assertEqual("Value error: Entity 'SOME ENTITY' not found in CarbuRe", context.exception.args[0])


class EntityNamesTest(TestCase):
    def test_format_entity_names(self):
        names = ["ENTITY 1", "ENTITY 2", "ENTITY 3"]
        entities = [EntityFactory.build(name=n) for n in names]
        self.assertEqual("entities 'ENTITY 1', 'ENTITY 2', 'ENTITY 3'", entity_names(entities))

    def test_format_entity_names_with_only_one_entity(self):
        entities = [EntityFactory.build(name="ENTITY 1")]
        self.assertEqual("entity 'ENTITY 1'", entity_names(entities))


class EntitiesNotInUDBTest(TestCase):
    def setUp(self):
        module = "edelivery.management.commands.export_national_scheme_certificates"
        self.patched_GetOrganisationByIDRequest = patch(f"{module}.GetOrganisationByIDRequest").start()
        self.patched_Requester = patch(f"{module}.Requester").start()
        self.patched_Requester.return_value.do_request.return_value = {}

    def tearDown(self):
        patch.stopall()

    def test_returns_entities_not_present_in_UDB(self):
        ntr_ids = ["NTR_ID_1", "NTR_ID_2", "NTR_ID_3"]
        entities = [MagicMock(**{"ntr_id.return_value": ntr_id}) for ntr_id in ntr_ids]
        request = "request"
        self.patched_GetOrganisationByIDRequest.return_value = request
        patched_do_request = self.patched_Requester.return_value.do_request
        patched_do_request.return_value = {"found_organisations": ["NTR_ID_2"]}

        self.patched_GetOrganisationByIDRequest.assert_not_called()
        self.patched_Requester.assert_not_called()
        patched_do_request.assert_not_called()

        result = find_entities_not_in_udb(entities)
        self.patched_GetOrganisationByIDRequest.assert_called_with("NTR_ID_1", "NTR_ID_2", "NTR_ID_3")
        call_args = self.patched_Requester.call_args
        self.assertEqual((request,), call_args.args)
        self.assertEqual(["NTR_ID_1", "NTR_ID_3"], [e.ntr_id() for e in result])

    def test_returns_entities_if_UDB_responds_not_found_error(self):
        entities = [MagicMock(**{"ntr_id.return_value": "NTR_ID_1"})]
        self.patched_Requester.return_value.do_request.return_value = {}

        result = find_entities_not_in_udb(entities)
        self.assertEqual(["NTR_ID_1"], [e.ntr_id() for e in result])

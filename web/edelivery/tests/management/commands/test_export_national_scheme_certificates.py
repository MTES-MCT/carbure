from unittest import TestCase
from unittest.mock import MagicMock, patch

from edelivery.management.commands.export_national_scheme_certificates import (
    carbure_entities,
    carbure_entity_certificates,
    certificate_ids,
    entity_names,
    export_certificates,
    export_entities,
    find_entities_not_in_udb,
)
from entity.factories.entity import EntityFactory
from transactions.factories.certificate import EntityCertificateFactory, GenericCertificateFactory


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
        query_result = [
            MagicMock(name="Entity 1", **{"ntr_id.return_value": "NTR_ID_1"}),
            MagicMock(name="Entity 2", **{"ntr_id.return_value": "NTR_ID_2"}),
        ]
        patched_all_currently_certified = self.patched_Entity.all_currently_certified_under_national_scheme
        patched_all_currently_certified.return_value = query_result
        patched_all_currently_certified.assert_not_called()

        (entities, _) = carbure_entities(fetch_all=True)
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

    def test_adds_error_messages_if_fetched_entities_in_error(self):
        self.patched_Entity.all_currently_certified_under_national_scheme.return_value = [
            MagicMock(**{"ntr_id.side_effect": RuntimeError("Oops")}),
            MagicMock(**{"ntr_id.side_effect": RuntimeError("Boom")}),
        ]

        with self.assertRaises(RuntimeError) as context:
            carbure_entities(fetch_all=True)

        self.assertEqual("No valid entity found: Oops; Boom", context.exception.args[0])

    def test_can_fetch_one_specific_carbure_entity_instead(self):
        query_result = [MagicMock(**{"ntr_id.return_value": "NTR_ID_1"})]
        patched_filter = self.patched_Entity.objects.filter
        patched_filter.return_value = query_result
        patched_filter.assert_not_called()

        (entity, _) = carbure_entities(entity_name="SOME ENTITY")
        patched_filter.assert_called_with(name="SOME ENTITY")
        self.assertEqual(query_result, entity)

    def test_raises_an_error_if_named_entity_not_found(self):
        patched_filter = self.patched_Entity.objects.filter
        patched_filter.return_value = []

        with self.assertRaises(RuntimeError) as context:
            carbure_entities(entity_name="SOME ENTITY")

        self.assertEqual("No entity to process: Entity 'SOME ENTITY' not found in CarbuRe", context.exception.args[0])

    def test_raises_an_error_when_error_encountered_on_single_fetched_entity(self):
        self.patched_Entity.objects.filter.return_value = [MagicMock(**{"ntr_id.side_effect": RuntimeError("Oops")})]

        with self.assertRaises(RuntimeError) as context:
            carbure_entities(entity_name="SOME ENTITY")

        self.assertEqual("No entity to process: Oops", context.exception.args[0])

    def test_returns_empty_error_log_if_no_error_encountered(self):
        self.patched_Entity.objects.filter.return_value = [MagicMock(**{"ntr_id.return_value": "NTR_ID_1"})]

        (_, errors) = carbure_entities(entity_name="SOME ENTITY")
        self.assertEqual([], errors)

    def test_handles_error_encountered(self):
        self.patched_Entity.all_currently_certified_under_national_scheme.return_value = [
            MagicMock(name="Entity 1", **{"ntr_id.side_effect": RuntimeError("Oops")}),
            MagicMock(name="Entity 2", **{"ntr_id.return_value": "NTR_ID_2"}),
        ]

        (result, errors) = carbure_entities(fetch_all=True)
        self.assertEqual(["NTR_ID_2"], [e.ntr_id() for e in result])
        self.assertEqual(["Oops"], errors)


class CarbureEntityCertificatesTest(TestCase):
    def setUp(self):
        module = "edelivery.management.commands.export_national_scheme_certificates"
        self.patched_EntityCertificate = patch(f"{module}.EntityCertificate").start()
        self.patched_valid_certificate_scope = patch(f"{module}.valid_certificate_scope", return_value=True).start()

    def tearDown(self):
        patch.stopall()

    def test_fetches_all_entity_certificates_for_entities_with_valid_national_scheme_certificate(self):
        query_result = [MagicMock(name="EC1")]
        patched_query = self.patched_EntityCertificate.all_for_entities_with_valid_national_scheme_certificate
        patched_query.return_value = query_result

        entities = MagicMock(name="entities")
        (entity_certificates, _) = carbure_entity_certificates(entities)
        patched_query.assert_called_with(entities)
        self.assertEqual(query_result, entity_certificates)

    def test_raises_an_error_if_no_certificate_found(self):
        self.patched_EntityCertificate.all_for_entities_with_valid_national_scheme_certificate.return_value = []

        with self.assertRaises(RuntimeError) as context:
            carbure_entity_certificates([EntityFactory.build(name="ENTITY 1")])

        self.assertEqual("No entity certificate found for entity 'ENTITY 1'", context.exception.args[0])

    def test_adds_error_messages_if_fetched_entity_certificates_in_error(self):
        self.patched_EntityCertificate.all_for_entities_with_valid_national_scheme_certificate.return_value = [
            MagicMock(
                name="EC1",
                **{
                    "certificate.certificate_id": "CERT_1",
                    "certificate.certificate_type": "TYPE_1",
                    "certificate.scope": "SCOPE_1",
                },
            ),
            MagicMock(
                name="EC2",
                **{
                    "certificate.certificate_id": "CERT_2",
                    "certificate.certificate_type": "TYPE_2",
                    "certificate.scope": "SCOPE_2",
                },
            ),
        ]
        self.patched_valid_certificate_scope.return_value = False

        with self.assertRaises(RuntimeError) as context:
            carbure_entity_certificates([EntityFactory.build(name="ENTITY 1")])

        self.patched_valid_certificate_scope.assert_any_call("TYPE_1", "SCOPE_1")
        self.patched_valid_certificate_scope.assert_any_call("TYPE_2", "SCOPE_2")
        self.assertEqual(
            "No valid entity certificate found for entity 'ENTITY 1': "
            "Scope invalid for certificate 'CERT_1'; "
            "Scope invalid for certificate 'CERT_2'",
            context.exception.args[0],
        )

    def test_only_keeps_valid_entity_certificates(self):
        self.patched_EntityCertificate.all_for_entities_with_valid_national_scheme_certificate.return_value = [
            MagicMock(name="EC1", **{"certificate.certificate_id": "CERT_1"}),
            MagicMock(name="EC2", **{"certificate.certificate_id": "CERT_2"}),
        ]
        self.patched_valid_certificate_scope.side_effect = [False, True]

        entities = [EntityFactory.build(name="ENTITY 1")]
        (entity_certificates, _) = carbure_entity_certificates(entities)
        self.assertEqual(["CERT_2"], [ec.certificate.certificate_id for ec in entity_certificates])

    def test_adds_encountered_errors_to_previous_errors(self):
        self.patched_EntityCertificate.all_for_entities_with_valid_national_scheme_certificate.return_value = [
            MagicMock(name="EC1", **{"certificate.certificate_id": "CERT_1"}),
            MagicMock(name="EC2", **{"certificate.certificate_id": "CERT_2"}),
        ]
        self.patched_valid_certificate_scope.side_effect = [False, True]

        entities = [EntityFactory.build(name="ENTITY 1")]
        previous_errors = ["Some error"]
        (_, errors) = carbure_entity_certificates(entities, previous_errors)
        self.assertEqual(["Some error", "Scope invalid for certificate 'CERT_1'"], errors)


class CertificateIdsTest(TestCase):
    def test_format_certificate_ids(self):
        ids = ["CERT_ID_1", "CERT_ID_2", "CERT_ID_3"]
        certificates = [GenericCertificateFactory.build(certificate_id=id) for id in ids]
        entity_certificates = [EntityCertificateFactory.build(certificate=c) for c in certificates]
        self.assertEqual("certificates 'CERT_ID_1', 'CERT_ID_2', 'CERT_ID_3'", certificate_ids(entity_certificates))

    def test_format_certificate_id_when_only_one_entity_certificate(self):
        certificate = GenericCertificateFactory.build(certificate_id="CERT_ID_1")
        entity_certificates = [EntityCertificateFactory.build(certificate=certificate)]
        self.assertEqual("certificate 'CERT_ID_1'", certificate_ids(entity_certificates))

    def test_format_certificate_ids_when_no_entity_certificate(self):
        self.assertEqual("no certificate", certificate_ids([]))


class EntityNamesTest(TestCase):
    def test_format_entity_names(self):
        names = ["ENTITY 1", "ENTITY 2", "ENTITY 3"]
        entities = [EntityFactory.build(name=n) for n in names]
        self.assertEqual("entities 'ENTITY 1', 'ENTITY 2', 'ENTITY 3'", entity_names(entities))

    def test_format_entity_names_with_only_one_entity(self):
        entities = [EntityFactory.build(name="ENTITY 1")]
        self.assertEqual("entity 'ENTITY 1'", entity_names(entities))

    def test_format_entity_names_if_no_entity(self):
        self.assertEqual("no entity", entity_names([]))


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


class ExportCertificates(TestCase):
    def setUp(self):
        module = "edelivery.management.commands.export_national_scheme_certificates"
        self.patched_EntityCertificate = patch(f"{module}.EntityCertificate").start()
        self.patched_AddUpdateCertificateRequest = patch(f"{module}.AddUpdateCertificateRequest").start()
        self.patched_Requester = patch(f"{module}.Requester").start()

    def tearDown(self):
        patch.stopall()

    def test_export_national_scheme_certificates(self):
        request = "request"
        self.patched_AddUpdateCertificateRequest.return_value = request
        patched_do_request = self.patched_Requester.return_value.do_request
        patched_do_request.return_value = {"responseStatus": "success"}

        self.patched_AddUpdateCertificateRequest.assert_not_called()
        self.patched_Requester.assert_not_called()
        patched_do_request.assert_not_called()

        entity_certificates = ["entity_certificate_1", "entity_certificate_2"]
        result = export_certificates(entity_certificates)
        self.patched_AddUpdateCertificateRequest.assert_called_with("entity_certificate_1", "entity_certificate_2")
        self.patched_Requester.assert_called()
        call_args = self.patched_Requester.call_args
        self.assertEqual((request,), call_args.args)
        patched_do_request.assert_called()
        self.assertEqual({"responseStatus": "success"}, result)


class ExportEntitiesTest(TestCase):
    def setUp(self):
        module = "edelivery.management.commands.export_national_scheme_certificates"
        self.patched_AddOrganisationRequest = patch(f"{module}.AddOrganisationRequest").start()
        self.patched_Requester = patch(f"{module}.Requester").start()

    def tearDown(self):
        patch.stopall()

    def test_exports_entities_not_in_udb(self):
        entities = ["entity_1", "entity_2"]
        request = "request"
        self.patched_AddOrganisationRequest.return_value = request
        patched_do_request = self.patched_Requester.return_value.do_request

        self.patched_AddOrganisationRequest.assert_not_called()
        self.patched_Requester.assert_not_called()
        patched_do_request.assert_not_called()

        export_entities(entities)
        self.patched_AddOrganisationRequest.assert_called_with("entity_1", "entity_2")
        call_args = self.patched_Requester.call_args
        self.assertEqual((request,), call_args.args)
        patched_do_request.assert_called()

    def test_does_not_request_udb_if_no_entity_to_create(self):
        export_entities([])
        self.patched_AddOrganisationRequest.assert_not_called()

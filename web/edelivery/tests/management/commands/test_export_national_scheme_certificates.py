from unittest import TestCase
from unittest.mock import MagicMock, patch

from core.models.certificate import GenericCertificate
from core.models.entity import Entity
from edelivery.management.commands.export_national_scheme_certificates import Command


class ExportNationalSchemeCertificatesTest(TestCase):
    def setUp(self):
        self.patched_Entity = patch("edelivery.management.commands.export_national_scheme_certificates.Entity").start()
        self.patched_GenericCertificate = patch("edelivery.management.commands.export_national_scheme_certificates.GenericCertificate").start()

    def tearDown(self):
        patch.stopall()

    def test_fetches_concerned_carbure_entities_through_all_valid_national_scheme_certificates(self):
        certificates = self.patched_GenericCertificate.all_valid_under_national_scheme.return_value
        query_result = MagicMock()
        patched_all_certified_with = self.patched_Entity.all_certified_with
        patched_all_certified_with.return_value = query_result

        command = Command()
        patched_all_certified_with.assert_not_called()

        entities = command.carbure_entities(export_all_certificates=True)
        patched_all_certified_with.assert_called_with(certificates)
        self.assertEqual(query_result, entities)




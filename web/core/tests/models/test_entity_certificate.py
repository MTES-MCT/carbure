from unittest import TestCase
from unittest.mock import MagicMock

from core.models.certificate import GenericCertificate
from core.models.entity_certificate import EntityCertificate


class EntityCertificateTest(TestCase):
    def test_fetches_all_records_for_given_entities_with_valid_national_scheme_certificate(self):
        entities = ["entity_1", "entity_2"]
        query_result = MagicMock()
        patched_filter = EntityCertificate.objects.filter = MagicMock(return_value=query_result)

        entity_certificates = EntityCertificate.all_for_entities_with_valid_national_scheme_certificate(entities)
        patched_filter.assert_called_with(
            entity__in=entities,
            certificate__certificate_type=GenericCertificate.SYSTEME_NATIONAL,
            certificate__status=GenericCertificate.VALID,
        )
        self.assertEqual(query_result, entity_certificates)

from unittest import TestCase
from unittest.mock import MagicMock, patch

from core.models.certificate import GenericCertificate
from core.models.entity import Entity
from core.models.geography import Pays


class EntityTest(TestCase):
    @patch("core.models.entity.Site")
    def test_knows_its_sites(self, patched_site):
        patched_filter = patched_site.objects.filter
        patched_filter.return_value = "some sites"

        entity = Entity()
        patched_filter.assert_not_called()

        result = entity.get_sites()
        patched_filter.assert_called_with(entitysite__entity=entity)
        self.assertEqual("some sites", result)

    @patch("core.models.entity.NationalTradeRegister")
    def test_includes_its_name_in_error_message_when_error_retrieving_NTR_id(self, patched_NationalTradeRegister):
        patched_ntr_id = patched_NationalTradeRegister.return_value.id
        patched_ntr_id.side_effect = NotImplementedError("oups")

        some_country = Pays()
        entity = Entity(name="The Entity", registered_country=some_country)
        with self.assertRaises(RuntimeError) as context:
            entity.ntr_id()

        self.assertEqual("Unable to retrieve NTR id for entity 'The Entity': oups", context.exception.args[0])

    def test_raises_exception_before_retrieving_NTR_id_if_no_registered_country(self):
        entity = Entity(name="The Entity")
        with self.assertRaises(ValueError) as context:
            entity.ntr_id()

        self.assertEqual("Entity 'The Entity' has no registered country", context.exception.args[0])

    def test_fetches_all_entities_currently_certified_under_national_scheme(self):
        query_result = MagicMock()
        patched_filter = Entity.objects.filter = MagicMock(return_value=query_result)

        entities = Entity.all_currently_certified_under_national_scheme()
        patched_filter.assert_called_with(
            entitycertificate__certificate__certificate_type=GenericCertificate.SYSTEME_NATIONAL,
            entitycertificate__certificate__status=GenericCertificate.VALID,
        )
        self.assertEqual(query_result, entities)

from unittest import TestCase
from unittest.mock import patch

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

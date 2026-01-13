from unittest import TestCase
from unittest.mock import patch

from core.models import Entity
from edelivery.ebms.ntr import from_national_trade_register


class FromNationalTradeRegisterTest(TestCase):
    def setUp(self):
        self.patched_Entity = patch("edelivery.ebms.ntr.Entity").start()

    def tearDown(self):
        patch.stopall()

    def test_fetches_entity_in_database(self):
        entity = Entity(name="Some Entity")
        patched_filter = self.patched_Entity.objects.filter
        patched_last = patched_filter.return_value.last
        patched_last.return_value = entity

        patched_filter.assert_not_called()
        patched_last.assert_not_called()

        result = from_national_trade_register("FR_SIREN_CD123456789")
        patched_filter.assert_called_with(registration_id="123456789")
        patched_last.assert_called()
        self.assertEqual("Some Entity", result.name)

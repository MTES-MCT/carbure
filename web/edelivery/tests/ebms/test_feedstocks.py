from unittest import TestCase
from unittest.mock import patch

from core.models import MatierePremiere
from edelivery.ebms.feedstocks import from_UDB_feedstock_code


class FromUDBFeedstockIdTest(TestCase):
    def setUp(self):
        self.patched_MatierePremiere = patch("edelivery.ebms.feedstocks.MatierePremiere").start()
        self.patched_MatierePremiere.objects.get.return_value = MatierePremiere()

    def tearDown(self):
        patch.stopall()

    def test_converts_UDB_sugar_beets_to_CarbuRe_feedstock(self):
        found_feedstock = MatierePremiere(code="BETTERAVE")
        get = self.patched_MatierePremiere.objects.get
        get.return_value = found_feedstock
        get.assert_not_called()

        carbure_feedstock = from_UDB_feedstock_code("URWS023")
        get.assert_called_with(code="BETTERAVE")
        self.assertEqual(found_feedstock, carbure_feedstock)

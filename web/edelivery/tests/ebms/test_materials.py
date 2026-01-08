from unittest import TestCase
from unittest.mock import patch

from core.models import Biocarburant, MatierePremiere
from edelivery.ebms.materials import from_UDB_biofuel_code, from_UDB_feedstock_code


class FromUDBBiofuelCodeTest(TestCase):
    def setUp(self):
        self.patched_Biocarburant = patch("edelivery.ebms.materials.Biocarburant").start()
        self.patched_Biocarburant.objects.get.return_value = Biocarburant()

    def tearDown(self):
        patch.stopall()

    def test_converts_UDB_biogas_to_CarbuRe_biofuel(self):
        found_biofuel = Biocarburant(code="BG")
        get = self.patched_Biocarburant.objects.get
        get.return_value = found_biofuel
        get.assert_not_called()

        carbure_biofuel = from_UDB_biofuel_code("SFC0015")
        get.assert_called_with(code="BG")
        self.assertEqual(found_biofuel, carbure_biofuel)


class FromUDBFeedstockCodeTest(TestCase):
    def setUp(self):
        self.patched_MatierePremiere = patch("edelivery.ebms.materials.MatierePremiere").start()
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

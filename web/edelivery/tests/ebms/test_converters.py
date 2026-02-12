from unittest import TestCase
from unittest.mock import patch

from core.models import Biocarburant, MatierePremiere
from edelivery.ebms.converters import MaterialConverter, QuantityConverter, UDBConversionError


class MaterialConverterTest(TestCase):
    def setUp(self):
        self.patched_Biocarburant = patch("edelivery.ebms.converters.Biocarburant").start()
        self.patched_Biocarburant.objects.get.return_value = Biocarburant()

        self.patched_MatierePremiere = patch("edelivery.ebms.converters.MatierePremiere").start()
        self.patched_MatierePremiere.objects.get.return_value = MatierePremiere()

    def tearDown(self):
        patch.stopall()

    def test_converts_udb_fame_to_carbure_biofuel(self):
        found_biofuel = Biocarburant(code="EMAG")
        get = self.patched_Biocarburant.objects.get
        get.return_value = found_biofuel

        converter = MaterialConverter({"FBM0003": "EMAG"})
        get.assert_not_called()

        carbure_biofuel = converter.from_udb_biofuel_code("FBM0003")
        get.assert_called_with(code="EMAG")
        self.assertEqual(found_biofuel, carbure_biofuel)

    def test_converts_udb_rapeseed_to_carbure_feedstock(self):
        found_feedstock = MatierePremiere(code="COLZA")
        get = self.patched_MatierePremiere.objects.get
        get.return_value = found_feedstock

        converter = MaterialConverter({"URWR001": "COLZA"})
        get.assert_not_called()

        carbure_feedstock = converter.from_udb_feedstock_code("URWR001")
        get.assert_called_with(code="COLZA")
        self.assertEqual(found_feedstock, carbure_feedstock)

    def test_raises_error_if_udb_code_unknown(self):
        converter = MaterialConverter({})
        with self.assertRaises(UDBConversionError) as context:
            converter.from_udb_feedstock_code("unknown_code")

        self.assertEqual("Unknown UDB Material code: unknown_code", context.exception.message)


class QuantityConverterTest(TestCase):
    def test_converts_udb_quantity_to_carbure_lot_attribute_value(self):
        conversion_mapping = {"UDB_UNIT": ("some_model_attribute", (lambda x: x * 2))}
        converter = QuantityConverter(conversion_mapping)
        self.assertEqual({"some_model_attribute": 20}, converter.from_udb("UDB_UNIT", 10))

    def test_raises_udb_conversion_error_if_unit_unknown(self):
        conversion_mapping = {"UDB_UNIT": ("some_model_attribute", (lambda x: x * 2))}
        converter = QuantityConverter(conversion_mapping)
        with self.assertRaises(UDBConversionError) as context:
            converter.from_udb("UNKNOWN_UNIT", 10)

        self.assertEqual("Unknown UDB Unit: UNKNOWN_UNIT", context.exception.message)

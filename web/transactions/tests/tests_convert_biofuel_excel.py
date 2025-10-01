from unittest import TestCase

from core.common import BiofuelExcelSerializer, convert_data_with_serializer


class ConvertBiofuelExcelTest(TestCase):
    def test_convert_with_default_values(self):
        row = {}
        result = convert_data_with_serializer(row, BiofuelExcelSerializer)
        assert result["carbure_stock_id"] == ""

    def test_convert_and_strip_values(self):
        row = {"carbure_stock_id": "  ABCD  "}
        result = convert_data_with_serializer(row, BiofuelExcelSerializer)
        assert result["carbure_stock_id"] == "ABCD"

    def test_convert_with_alias(self):
        row = {"champ_libre": "ABCD"}
        result = convert_data_with_serializer(row, BiofuelExcelSerializer)
        assert result["free_field"] == "ABCD"

from unittest import TestCase

from core.models import Biocarburant, CarbureLot, GenericError
from transactions.helpers import check_lot_info, fill_basic_info


class FillBasicInfoTest(TestCase):
    def test_return_error_when_prefetched_data_is_missing(self):
        lot = CarbureLot()
        form_data = {}

        prefetched_data = {
            "biofuels": None,
            "feedstocks": None,
            "countries": None,
        }

        errors = fill_basic_info(lot, form_data, prefetched_data)

        self.assertGreater(len(errors), 0)
        self.assertIsInstance(errors[0], GenericError)
        self.assertEqual(errors[0].error, "MISSING_BIOFUEL")

    def test_report_missing_field(self):
        form_data = {}
        prefetched_data = {"some_field": None}

        config = {
            "form_key": "biofuel_code",
            "prefetched_key": "biofuels",
            "missing_code_error": "MISSING_BIOFUEL",
        }

        result = check_lot_info(config, form_data, prefetched_data)

        self.assertEqual(result.error, "MISSING_BIOFUEL")
        self.assertEqual(result.field, "biofuel_code")
        self.assertEqual(result.is_blocking, True)

    def test_report_unknown_field(self):
        prefetched_data = {"biofuels": []}
        form_data = {"biofuel_code": "ETH"}

        config = {
            "form_key": "biofuel_code",
            "prefetched_key": "biofuels",
            "unknown_code_error": "UNKNOWN_BIOFUEL",
        }

        result = check_lot_info(config, form_data, prefetched_data)

        self.assertEqual(result.error, "UNKNOWN_BIOFUEL")
        self.assertEqual(result.field, "biofuel_code")
        self.assertEqual(result.is_blocking, True)

    def test_extract_known_field(self):
        prefetched_data = {"biofuels": {"ETH": Biocarburant(code="ETH")}}
        form_data = {"biofuel_code": "ETH"}

        config = {
            "form_key": "biofuel_code",
            "prefetched_key": "biofuels",
        }

        result = check_lot_info(config, form_data, prefetched_data)

        self.assertEqual(result, Biocarburant(code="ETH"))

from unittest import TestCase

from core.models import CarbureLot, GenericError
from transactions.helpers import fill_basic_info


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
        def check_lot_info(config, form_data, prefetched_data):
            return GenericError(error="SOME ERROR")

        form_data = {}
        prefetched_data = {"some_field": None}
        config = {"field_name": "some_field", "missing_error_label": "SOME ERROR"}
        result = check_lot_info(config, form_data, prefetched_data)
        self.assertEqual(result.error, "SOME ERROR")

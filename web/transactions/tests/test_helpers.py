from datetime import date
from unittest import TestCase

from core.models import CarbureLot, Entity
from transactions.helpers import INCORRECT_FORMAT_DISPATCH_DATE, construct_carbure_lot, fill_dispatch_data, fill_usage_data
from transactions.models import Site
from transactions.sanity_checks.mandatory import check_missing_usage, check_missing_usage_precision_for_other_usage


class UsageFieldsTest(TestCase):
    def test_usage_fields_for_delivery_types(self):
        for delivery_type in (CarbureLot.RFC, CarbureLot.DIRECT, CarbureLot.EXPORT):
            with self.subTest(delivery_type=delivery_type):
                lot = CarbureLot(delivery_type=delivery_type)
                relevant = delivery_type != CarbureLot.EXPORT
                self.assertEqual(check_missing_usage(lot) is not None, relevant)

                fill_usage_data(lot, {"usage": CarbureLot.USAGE_OTHER, "usage_precision": "Details"})
                self.assertEqual(lot.usage, CarbureLot.USAGE_OTHER if relevant else "")
                self.assertEqual(lot.usage_precision, "Details" if relevant else "")
                self.assertIsNone(check_missing_usage(lot))
                self.assertIsNone(check_missing_usage_precision_for_other_usage(lot))

                lot.usage_precision = ""
                self.assertEqual(check_missing_usage_precision_for_other_usage(lot) is not None, relevant)

                fill_usage_data(lot, {"usage": CarbureLot.USAGE_ROAD, "usage_precision": "Details"})
                self.assertEqual(lot.usage, CarbureLot.USAGE_ROAD if relevant else "")
                self.assertEqual(lot.usage_precision, "")
                self.assertIsNone(check_missing_usage_precision_for_other_usage(lot))


class ConstructCarbureLotTest(TestCase):
    def setUp(self):
        self.prefetched_data = {"biofuels": [], "countries": {}, "depots": [], "feedstocks": [], "sites": {}}

    def test_includes_udb_transaction_id_to_constructed_lot(self):
        data = {"udb_transaction_id": "12345"}
        lot, _ = construct_carbure_lot(self.prefetched_data, Entity(), data)
        self.assertEqual("12345", lot.udb_transaction_id)

    def test_includes_dispatch_date_to_constructed_lot(self):
        data = {"dispatch_date": date(2026, 3, 13)}
        lot, _ = construct_carbure_lot(self.prefetched_data, Entity(), data)
        self.assertEqual(date(2026, 3, 13), lot.dispatch_date)

    def test_returns_error_for_invalid_dispatch_date(self):
        data = {"dispatch_date": "not-a-date"}
        lot, errors = construct_carbure_lot(self.prefetched_data, Entity(), data)

        dispatch_errors = [error for error in errors if error.field == "dispatch_date"]
        self.assertEqual(1, len(dispatch_errors))
        self.assertEqual(INCORRECT_FORMAT_DISPATCH_DATE, dispatch_errors[0].error)
        self.assertTrue(dispatch_errors[0].is_blocking)

    def test_allows_missing_or_unknown_dispatch_site_id(self):
        for site_id in (None, "", 999, "not-an-id"):
            with self.subTest(site_id=site_id):
                lot = CarbureLot(carbure_dispatch_site=Site(pk=1, site_type=Site.EFPE))
                errors = fill_dispatch_data(
                    lot,
                    {"carbure_dispatch_site_id": site_id, "unknown_dispatch_site": "Unknown Dispatch Site"},
                    self.prefetched_data,
                )

                self.assertEqual([], errors)
                self.assertIsNone(lot.carbure_dispatch_site)
                self.assertIsNone(lot.dispatch_site_country)
                self.assertEqual("Unknown Dispatch Site", lot.unknown_dispatch_site)

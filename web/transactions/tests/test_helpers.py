from datetime import date
from unittest import TestCase

from core.models import Entity
from transactions.helpers import INCORRECT_FORMAT_DISPATCH_DATE, construct_carbure_lot


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

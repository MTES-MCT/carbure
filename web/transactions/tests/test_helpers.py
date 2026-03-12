from datetime import date
from unittest import TestCase

from core.models import Entity
from transactions.helpers import construct_carbure_lot


class ConstructCarbureLotTest(TestCase):
    def setUp(self):
        self.prefetched_data = {"biofuels": [], "countries": [], "depots": [], "feedstocks": []}

    def test_includes_udb_transaction_id_to_constructed_lot(self):
        data = {"udb_transaction_id": "12345"}
        lot, _ = construct_carbure_lot(self.prefetched_data, Entity(), data)
        self.assertEqual("12345", lot.udb_transaction_id)

    def test_includes_dispatch_date_to_constructed_lot(self):
        data = {"dispatch_date": date(2026, 3, 13)}
        lot, _ = construct_carbure_lot(self.prefetched_data, Entity(), data)
        self.assertEqual(date(2026, 3, 13), lot.dispatch_date)

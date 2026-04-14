from unittest import TestCase

from core.traceability.lot import LotNode


class LotNodeTest(TestCase):
    def test_accepts_dispatch_date_as_updatable_field(self):
        self.assertIn("dispatch_date", LotNode.TRADING_FIELDS)

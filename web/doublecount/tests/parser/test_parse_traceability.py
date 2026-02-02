from unittest import TestCase
from unittest.mock import MagicMock, patch

from doublecount.parser.parse_traceability import parse_traceability


class ParseTraceabilityTest(TestCase):
    def setUp(self):
        self.patched_log_exception = patch("doublecount.parser.parse_traceability.log_exception").start()

    def tearDown(self):
        patch.stopall()

    def test_logs_errors_to_Sentry_on_Excel_parsing_error_and_proceeds(self):
        self.patched_log_exception.assert_not_called()

        e = Exception("oops")
        excel_file = MagicMock()
        excel_file.__getitem__.side_effect = e
        result = parse_traceability(excel_file)
        self.patched_log_exception.assert_called_with(e)
        self.assertEqual({"before": None, "on_site": None, "after": None}, result)

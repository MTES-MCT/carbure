from unittest import TestCase
from unittest.mock import MagicMock, patch

from doublecount.parser.parse_info import parse_info


class ParseInfoTest(TestCase):
    def setUp(self):
        self.patched_log_exception = patch("doublecount.parser.parse_info.log_exception").start()

    def tearDown(self):
        patch.stopall()

    def test_logs_errors_to_Sentry_on_Excel_parsing_error_and_proceeds(self):
        self.patched_log_exception.assert_not_called()

        e = Exception("oops")
        excel_file = MagicMock()
        excel_file.__getitem__.side_effect = e
        result = parse_info(excel_file)
        self.patched_log_exception.assert_called_with(e)
        self.assertEqual({"production_site": None, "producer_email": None, "start_year": 0}, result)

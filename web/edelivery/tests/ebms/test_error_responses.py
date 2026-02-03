from unittest import TestCase
from unittest.mock import patch

from edelivery.ebms.error_responses import InvalidRequestErrorResponse, NotFoundErrorResponse, UnknownStatusErrorResponse


class InvalidRequestErrorResponseTest(TestCase):
    @staticmethod
    def payload(message="Error!"):
        return f"""\
<?xml version="1.0" encoding="UTF-8"?>
<udb:ErrorResponse xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <RESPONSE_HEADER REQUEST_ID="123" STATUS="INVALID_REQUEST" OBSERVATION="{message}" />
</udb:ErrorResponse>"""

    def test_knows_its_error_message(self):
        response = InvalidRequestErrorResponse(self.payload(message="Oops"))
        self.assertEqual("Oops", response.error_message())

    @patch("edelivery.ebms.error_responses.log_error")
    def test_sends_sentry_alert_as_post_retrieval_action(self, patched_log_error):
        response = InvalidRequestErrorResponse(self.payload(message="Oops"))
        patched_log_error.assert_not_called()

        result = response.post_retrieval_action_result()
        patched_log_error.assert_called_with("Invalid request", {"error": "Oops"})
        self.assertEqual({"error": "Invalid request", "message": "Oops"}, result)


class NotFoundErrorResponseTest(TestCase):
    @staticmethod
    def payload():
        return """\
<udb:EOGetTransactionResponse
  xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <RESPONSE_HEADER REQUEST_ID="123" STATUS="NOT_FOUND" />
  <!-- … -->
</udb:EOGetTransactionResponse>"""

    @patch("edelivery.ebms.error_responses.log_error")
    def test_sends_sentry_alert_as_post_retrieval_action(self, patched_log_error):
        response = NotFoundErrorResponse(self.payload())
        patched_log_error.assert_not_called()

        result = response.post_retrieval_action_result()
        patched_log_error.assert_called_with("Search returned no result")
        self.assertEqual({"error": "Not found"}, result)


class UnknownStatusErrorResponseTest(TestCase):
    @staticmethod
    def payload(status="SOME_ERROR_STATUS"):
        return f"""\
<?xml version="1.0" encoding="UTF-8"?>
<udb:ErrorResponse xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <RESPONSE_HEADER REQUEST_ID="123" STATUS="{status}" />
</udb:ErrorResponse>"""

    def test_knows_its_status(self):
        response = UnknownStatusErrorResponse(self.payload(status="SOME_UNKNOWN_STATUS"))
        self.assertEqual("SOME_UNKNOWN_STATUS", response.status())

    @patch("edelivery.ebms.error_responses.log_error")
    def test_logs_error_as_post_retrieval_action(self, patched_log_error):
        response = UnknownStatusErrorResponse(self.payload(status="SOME_UNKNOWN_STATUS"))
        patched_log_error.assert_not_called()

        result = response.post_retrieval_action_result()
        patched_log_error.assert_called_with("Received UDB response with unknown status", {"status": "SOME_UNKNOWN_STATUS"})
        self.assertEqual({"error": "Unknown response status", "status": "SOME_UNKNOWN_STATUS"}, result)

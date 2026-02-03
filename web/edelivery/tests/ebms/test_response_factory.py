from unittest import TestCase

from edelivery.ebms.request_responses import (
    BaseRequestResponse,
    InvalidRequestErrorResponse,
    NotFoundErrorResponse,
    UnknownStatusErrorResponse,
)
from edelivery.ebms.response_factory import ResponseFactory


class ResponseFactoryTest(TestCase):
    @staticmethod
    def payload(status="FOUND"):
        return f"""\
<udb:EOGetTransactionResponse
  xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <RESPONSE_HEADER REQUEST_ID="123"
                   STATUS="{status}" />
  <!-- … -->
</udb:EOGetTransactionResponse>"""

    def test_knows_UDB_response_status(self):
        factory = ResponseFactory(BaseRequestResponse, self.payload(status="SOME_STATUS"))
        self.assertEqual("SOME_STATUS", factory.udb_response_status())

    def test_returns_a_request_response_with_found_data_on_UDB_response_status_found(self):
        factory = ResponseFactory(BaseRequestResponse, self.payload())
        response = factory.response()
        self.assertIsInstance(response, BaseRequestResponse)
        self.assertEqual(self.payload(), response.payload)

    def test_returns_an_error_response_on_UDB_response_status_not_found(self):
        factory = ResponseFactory(BaseRequestResponse, self.payload(status="NOT_FOUND"))
        response = factory.response()
        self.assertIsInstance(response, NotFoundErrorResponse)

    def test_returns_an_error_response_on_UDB_response_status_invalid_request(self):
        factory = ResponseFactory(BaseRequestResponse, self.payload(status="INVALID_REQUEST"))
        response = factory.response()
        self.assertIsInstance(response, InvalidRequestErrorResponse)

    def test_returns_an_error_response_on_UDB_response_with_unknown_status(self):
        factory = ResponseFactory(BaseRequestResponse, self.payload(status="UNKNOWN_STATUS"))
        response = factory.response()
        self.assertIsInstance(response, UnknownStatusErrorResponse)

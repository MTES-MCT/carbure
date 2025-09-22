from unittest import TestCase
from unittest.mock import MagicMock

from edelivery.soap.actions import ListPendingMessages
from edelivery.soap.responses import ListPendingMessagesResponse


class ListPendingMessagesTest(TestCase):
    def setUp(self):
        self.http_response = MagicMock()
        self.http_response.text = "<response/>"

        self.send_callback = MagicMock()
        self.send_callback.return_value = self.http_response

    def test_sends_payload_to_eDelivery_service(self):
        action = ListPendingMessages(self.send_callback)
        action.perform()

        expectedPayload = """\
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:_1="http://eu.domibus.wsplugin/">
  <soap:Header/>
  <soap:Body>
    <_1:listPendingMessagesRequest></_1:listPendingMessagesRequest>
  </soap:Body>
</soap:Envelope>"""
        self.send_callback.assert_called_with(action="listPendingMessages", payload=expectedPayload)

    def test_returns_a_ListPendingMessagesResponse_as_result(self):
        self.http_response.text = "<response>some response</response>"
        action = ListPendingMessages(self.send_callback)
        result = action.perform()

        self.assertIsInstance(result, ListPendingMessagesResponse)
        self.assertEqual(result.text, "<response>some response</response>")

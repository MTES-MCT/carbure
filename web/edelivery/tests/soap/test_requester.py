from unittest import TestCase
from unittest.mock import patch

from edelivery.ebms.request_responses import EOGetTransactionResponse
from edelivery.ebms.requests import BaseRequest, EOGetTransactionRequest
from edelivery.soap.requester import Requester


@patch.dict("os.environ", {"UDB_ACCESS_POINT_ID": "UDB"})
class RequesterTest(TestCase):
    DEFAULT_RESPONSE_PAYLOAD = """\
<udb:RequestResponse xmlns:udb="http://udb.example.com">
  <RESPONSE_HEADER REQUEST_ID="111"/>
  <!-- … -->
</udb:RequestResponse>"""

    def setUp(self):
        patch("edelivery.soap.requester.sleep").start()
        self.patched_PubSubAdapter = patch("edelivery.soap.requester.PubSubAdapter").start()
        self.patched_SubmitMessage = patch("edelivery.soap.requester.SubmitMessage").start()
        self.patched_PubSubAdapter.return_value.next_message.return_value = self.DEFAULT_RESPONSE_PAYLOAD

        self.patched_new_uuid = patch("edelivery.ebms.requests.new_uuid").start()

    def tearDown(self):
        patch.stopall()

    def test_subscribes_to_message_queue_before_submitting_request(self):
        commands_called = []
        self.patched_PubSubAdapter.return_value.subscribe = lambda: commands_called.append("subscribe")
        self.patched_SubmitMessage.return_value.perform = lambda: commands_called.append("submit request")
        self.patched_new_uuid.return_value = "111"

        request = BaseRequest("<request/>")
        requester = Requester(request)
        self.assertEqual([], commands_called)

        requester.response()
        self.assertEqual(["subscribe", "submit request"], commands_called)

    def test_unsubscribes_to_message_queue_after_fetching_message(self):
        commands_called = []

        def log_next_message_call():
            commands_called.append("fetch message")
            return self.DEFAULT_RESPONSE_PAYLOAD

        self.patched_PubSubAdapter.return_value.next_message = log_next_message_call
        self.patched_PubSubAdapter.return_value.unsubscribe = lambda: commands_called.append("unsubscribe")
        self.patched_new_uuid.return_value = "111"

        request = BaseRequest("<request/>")
        requester = Requester(request)
        self.assertEqual([], commands_called)

        requester.response()
        self.assertEqual(["fetch message", "unsubscribe"], commands_called)

    def test_returns_request_response_received_from_udb(self):
        self.patched_PubSubAdapter.return_value.next_message.return_value = self.DEFAULT_RESPONSE_PAYLOAD
        self.patched_new_uuid.return_value = "111"
        request = BaseRequest("<request/>")
        requester = Requester(request)

        response = requester.response()
        self.assertEqual(self.DEFAULT_RESPONSE_PAYLOAD, response.payload)

    def test_returns_response_class_corresponding_to_request_class(self):
        self.patched_new_uuid.return_value = "111"
        request = EOGetTransactionRequest("12345")
        requester = Requester(request)

        response = requester.response()
        self.assertIsInstance(response, EOGetTransactionResponse)

    def test_throws_timeout_error_if_not_receiving_any_response_from_udb(self):
        self.patched_PubSubAdapter.return_value.next_message.return_value = None
        request = BaseRequest("<request/>")
        requester = Requester(request, delay_between_retries=0.001, timeout=0.002)

        self.assertRaises(TimeoutError, requester.response)

    def test_retries_few_times_before_throwing_timeout_error(self):
        self.patched_PubSubAdapter.return_value.next_message.side_effect = [None, self.DEFAULT_RESPONSE_PAYLOAD]
        self.patched_new_uuid.return_value = "111"
        request = BaseRequest("<request/>")
        requester = Requester(request)

        response = requester.response()
        self.assertEqual(self.DEFAULT_RESPONSE_PAYLOAD, response.payload)

    @patch("edelivery.ebms.requests.new_uuid")
    def test_checks_whether_request_ids_correspond(self, patched_new_uuid):
        self.patched_PubSubAdapter.return_value.next_message.return_value = self.DEFAULT_RESPONSE_PAYLOAD
        self.patched_new_uuid.return_value = "different_request_id"
        request = BaseRequest("<request/>")
        requester = Requester(request, delay_between_retries=0.001, timeout=0.002)

        self.assertRaises(TimeoutError, requester.response)

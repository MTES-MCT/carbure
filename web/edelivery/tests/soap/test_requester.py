import json
from unittest import TestCase
from unittest.mock import patch

from edelivery.ebms.request_responses.base_request_response import BaseRequestResponse
from edelivery.ebms.requests.base_request import BaseRequest
from edelivery.soap.requester import Requester


class MockResponse:
    def __init__(self, post_retrieval_action_result_value):
        self.post_retrieval_action_result_value = post_retrieval_action_result_value

    def post_retrieval_action_result(self):
        return self.post_retrieval_action_result_value


MATCHING_ID = "111"


@patch.dict("os.environ", {"UDB_ACCESS_POINT_ID": "UDB"})
class RequesterTest(TestCase):
    @staticmethod
    def message_received(conversation_id=MATCHING_ID, payload="<defaultResponse/>"):
        return json.dumps({"conversation_id": conversation_id, "payload": payload})

    def setUp(self):
        patch("edelivery.soap.requester.sleep").start()
        self.patched_PubSubAdapter = patch("edelivery.soap.requester.PubSubAdapter").start()
        self.patched_SubmitMessage = patch("edelivery.soap.requester.SubmitMessage").start()
        self.patched_PubSubAdapter.return_value.next_message.return_value = self.message_received()

        self.patched_new_uuid = patch("edelivery.ebms.requests.base_request.new_uuid").start()
        self.patched_new_uuid.return_value = MATCHING_ID

        self.patched_ResponseFactory = patch("edelivery.soap.requester.ResponseFactory").start()
        self.patched_ResponseFactory.return_value.response.return_value = MockResponse("Some result")

    def tearDown(self):
        patch.stopall()

    def test_subscribes_to_message_queue_before_submitting_request(self):
        commands_called = []
        self.patched_PubSubAdapter.return_value.subscribe = lambda: commands_called.append("subscribe")
        self.patched_SubmitMessage.return_value.perform = lambda: commands_called.append("submit request")

        request = BaseRequest("<request/>")
        requester = Requester(request)
        self.assertEqual([], commands_called)

        requester.do_request()
        self.assertEqual(["subscribe", "submit request"], commands_called)

    def test_unsubscribes_to_message_queue_after_fetching_message(self):
        commands_called = []

        def log_next_message_call():
            commands_called.append("fetch message")
            return self.message_received()

        self.patched_PubSubAdapter.return_value.next_message = log_next_message_call
        self.patched_PubSubAdapter.return_value.unsubscribe = lambda: commands_called.append("unsubscribe")

        request = BaseRequest("<request/>")
        requester = Requester(request)
        self.assertEqual([], commands_called)

        requester.do_request()
        self.assertEqual(["fetch message", "unsubscribe"], commands_called)

    def test_instantiates_response_object_with_proper_class_and__received_message(self):
        self.patched_PubSubAdapter.return_value.next_message.return_value = self.message_received(payload="<response/>")

        request = BaseRequest("<request/>")
        requester = Requester(request)
        self.patched_ResponseFactory.assert_not_called()

        requester.do_request()
        self.patched_ResponseFactory.assert_called_with(BaseRequestResponse, "<response/>")

    def test_returns_result_of_action_triggered_upon_receiving_response_from_udb(self):
        self.patched_ResponseFactory.return_value.response.return_value = MockResponse("Some result")

        request = BaseRequest("<request/>")
        requester = Requester(request)
        result = requester.do_request()
        self.assertEqual("Some result", result)

    def test_throws_timeout_error_if_not_receiving_any_response_from_udb(self):
        self.patched_PubSubAdapter.return_value.next_message.return_value = None
        request = BaseRequest("<request/>")
        requester = Requester(request, delay_between_retries=0.001, timeout=0.002)

        self.assertRaises(TimeoutError, requester.do_request)

    def test_retries_few_times_before_throwing_timeout_error(self):
        self.patched_ResponseFactory.return_value.response.return_value = MockResponse("Some result")
        self.patched_PubSubAdapter.return_value.next_message.side_effect = [None, self.message_received()]

        request = BaseRequest("<request/>")
        requester = Requester(request)
        result = requester.do_request()
        self.assertEqual("Some result", result)

    @patch("edelivery.ebms.requests.base_request.new_uuid")
    def test_checks_whether_conversation_ids_correspond(self, patched_new_uuid):
        self.patched_PubSubAdapter.return_value.next_message.return_value = self.message_received(
            conversation_id="different_id",
        )
        request = BaseRequest("<request/>")
        requester = Requester(request, delay_between_retries=0.001, timeout=0.002)

        self.assertRaises(TimeoutError, requester.do_request)

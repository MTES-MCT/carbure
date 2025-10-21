from unittest import TestCase
from unittest.mock import Mock, patch

from edelivery.soap.listener import Listener


class ListenerTest(TestCase):
    def setUp(self):
        self.patched_ListPendingMessages = patch("edelivery.soap.listener.ListPendingMessages").start()
        self.patched_PubSubAdapter = patch("edelivery.soap.listener.PubSubAdapter").start()
        self.patched_RetrieveMessage = patch("edelivery.soap.listener.RetrieveMessage").start()
        self.patched_sleep = patch("edelivery.soap.listener.sleep").start()

    def tearDown(self):
        patch.stopall()

    def test_checks_whether_pending_messages(self):
        perform = self.patched_ListPendingMessages.return_value.perform

        listener = Listener()
        perform.assert_not_called()

        listener.poll_once()
        perform.assert_called()

    def test_fetches_next_pending_message_if_one_present(self):
        list_perform = self.patched_ListPendingMessages.return_value.perform
        list_perform.return_value.pending_message_present = Mock(return_value=True)
        list_perform.return_value.next_pending_message_id = Mock(return_value="123")

        retrieve_perform = self.patched_RetrieveMessage.return_value.perform

        listener = Listener()
        self.patched_RetrieveMessage.assert_not_called()

        listener.poll_once()
        self.patched_RetrieveMessage.assert_called_with("123")
        retrieve_perform.assert_called()

    def test_publishes_retrieved_message_on_message_queue(self):
        perform = self.patched_RetrieveMessage.return_value.perform
        perform.return_value.request_response_payload = "<response/>"

        publish = self.patched_PubSubAdapter.return_value.publish

        listener = Listener()
        publish.assert_not_called()

        listener.poll_once()
        publish.assert_called_with("<response/>")

    def test_starts_when_asked_and_polls_eDelivery_layer_every_second(self):
        commands_called = []

        def log_list_pending_messages_call():
            commands_called.append("list")
            return Mock()

        self.patched_ListPendingMessages.return_value.perform = log_list_pending_messages_call
        self.patched_sleep.side_effect = [None, None, Warning()]

        try:
            listener = Listener()
            self.assertEqual([], commands_called)
            listener.start()

            self.fail("sleep() should have been called")
        except Warning:
            self.patched_sleep.assert_called_with(1)
            self.assertEqual(["list", "list", "list"], commands_called)

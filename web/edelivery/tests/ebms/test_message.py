from unittest import TestCase
from unittest.mock import patch

from edelivery.ebms.messages import Message


@patch.dict("os.environ", {"INITIATOR_ACCESS_POINT_ID": "initiator_id"})
class MessageTest(TestCase):
    def setUp(self):
        self.patched_new_uuid = patch("edelivery.ebms.messages.new_uuid").start()
        self.patched_timestamp = patch("edelivery.ebms.messages.timestamp").start()

    def tearDown(self):
        patch.stopall()

    def test_has_a_UUID(self):
        self.patched_new_uuid.return_value = "12345678-1234-1234-1234-1234567890ab"

        message = Message("responder_id", "A request")
        self.assertEqual("12345678-1234-1234-1234-1234567890ab", message.identifier())

    def test_has_a_timestamp(self):
        self.patched_timestamp.return_value = "2025-07-15T13:00:00+00:00"

        message = Message("responder_id", "A request")
        self.assertEqual("2025-07-15T13:00:00+00:00", message.timestamp)

    def test_knows_initiator(self):
        message = Message("responder_id", "A request")
        self.assertEqual("initiator_id", message.initiator_id())

    @patch("edelivery.ebms.messages.encode")
    def test_encodes_its_body(self, patched_encode):
        patched_encode.return_value = "abcdef"
        message = Message("responder_id", "A request")

        encoded_message = message.encoded()
        patched_encode.assert_called_with("A request")
        self.assertEqual("abcdef", encoded_message)

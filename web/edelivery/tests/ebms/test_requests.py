from os import environ
from unittest import TestCase
from unittest.mock import patch

from edelivery.ebms.requests import BaseRequest


@patch.dict("os.environ", {"INITIATOR_ACCESS_POINT_ID": "initiator_id", "CARBURE_NTR": "CarbuRe_NTR"})
class BaseRequestTest(TestCase):
    def setUp(self):
        self.patched_new_uuid = patch("edelivery.ebms.requests.new_uuid").start()
        self.patched_timestamp = patch("edelivery.ebms.requests.timestamp").start()

    def tearDown(self):
        patch.stopall()

    def test_has_a_UUID(self):
        self.patched_new_uuid.return_value = "12345678-1234-1234-1234-1234567890ab"

        request = BaseRequest("responder_id", "A request")
        self.assertEqual("12345678-1234-1234-1234-1234567890ab", request.identifier())

    def test_has_a_timestamp(self):
        self.patched_timestamp.return_value = "2025-07-15T13:00:00+00:00"

        request = BaseRequest("responder_id", "A request")
        self.assertEqual("2025-07-15T13:00:00+00:00", request.timestamp)

    def test_knows_initiator(self):
        self.assertEqual("initiator_id", environ["INITIATOR_ACCESS_POINT_ID"])

        request = BaseRequest("responder_id", "A request")
        self.assertEqual("initiator_id", request.initiator_id())

    def test_knows_original_sender(self):
        self.assertEqual("CarbuRe_NTR", environ["CARBURE_NTR"])

        request = BaseRequest("responder_id", "A request")
        self.assertEqual("CarbuRe_NTR", request.original_sender)

    @patch("edelivery.ebms.requests.zip_and_stream_udb_request")
    def test_zips_and_encodes_its_body(self, patched_zip_and_stream_udb_request):
        patched_zip_and_stream_udb_request.return_value = "abcdef"
        request = BaseRequest("responder_id", "A request")

        encoded_request = request.zipped_encoded()
        patched_zip_and_stream_udb_request.assert_called_with("A request")
        self.assertEqual("abcdef", encoded_request)

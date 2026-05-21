from unittest import TestCase
from unittest.mock import patch

from edelivery.ebms.request_responses.base_request_response import BaseRequestResponse
from edelivery.ebms.requests.base_request import BaseRequest


class BaseRequestTest(TestCase):
    def setUp(self):
        self.patched_new_uuid = patch("edelivery.ebms.requests.base_request.new_uuid").start()
        self.patched_new_uuid.return_value = "12345678-1234-1234-1234-1234567890ab"

    def tearDown(self):
        patch.stopall()

    def test_inserts_request_id(self):
        self.assertEqual("12345678-1234-1234-1234-1234567890ab", self.patched_new_uuid())

        request = BaseRequest("<request/>")
        expected_body = """\
<request>
  <REQUEST_HEADER REQUEST_ID="12345678-1234-1234-1234-1234567890ab" />
</request>"""
        self.assertEqual(request.body, expected_body)

    @patch("edelivery.ebms.requests.base_request.zip_and_stream_udb_request")
    def test_zips_and_encodes_its_body(self, patched_zip_and_stream_udb_request):
        self.assertEqual("12345678-1234-1234-1234-1234567890ab", self.patched_new_uuid())

        patched_zip_and_stream_udb_request.return_value = "abcdef"
        request = BaseRequest("<request/>")

        encoded_request = request.zipped_encoded()
        expected_body = """\
<request>
  <REQUEST_HEADER REQUEST_ID="12345678-1234-1234-1234-1234567890ab" />
</request>"""
        patched_zip_and_stream_udb_request.assert_called_with(expected_body)
        self.assertEqual("abcdef", encoded_request)

    def test_knows_its_response_class(self):
        request = BaseRequest("<request/>")
        self.assertEqual(BaseRequestResponse, request.response_class)

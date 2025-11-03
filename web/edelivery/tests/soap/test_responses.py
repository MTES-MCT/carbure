from unittest import TestCase
from unittest.mock import patch

from edelivery.ebms.request_responses import BaseRequestResponse
from edelivery.soap.responses import ListPendingMessagesResponse, RetrieveMessageResponse, SubmitMessageResponse


class ListPendingMessagesResponseTest(TestCase):
    def response_payload(_, message_ids):
        message_ids_to_XML = [f"""<messageID>{id}</messageID>""" for id in message_ids]

        return f"""\
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Body>
    <ns4:listPendingMessagesResponse xmlns:ns4="http://eu.domibus.wsplugin/">
      {message_ids_to_XML}
    </ns4:listPendingMessagesResponse>
  </soap:Body>
</soap:Envelope>"""

    def test_parses_next_pending_message_id(self):
        payload = self.response_payload(["123", "456"])
        response = ListPendingMessagesResponse(payload)

        self.assertTrue(response.pending_message_present())
        self.assertEqual(response.next_pending_message_id(), "123")

    def test_checks_whether_no_pending_message(self):
        payload = self.response_payload([])
        response = ListPendingMessagesResponse(payload)

        self.assertFalse(response.pending_message_present())


class RetrieveMessageResponseTest(TestCase):
    def response_payload(_self, attachment_value=""):
        return f"""\
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Header>
    <!-- … -->
  </soap:Header>
  <soap:Body>
    <ns4:retrieveMessageResponse xmlns:ns4="http://eu.domibus.wsplugin/">
      <payload payloadId="cid:attachment" contentType="application/octet-stream">
        <value>{attachment_value}</value>
      </payload>
    </ns4:retrieveMessageResponse>
  </soap:Body>
</soap:Envelope>"""

    def setUp(self):
        self.patched_unzip = patch("edelivery.soap.responses.unzip_base64_encoded_stream").start()

    def tearDown(self):
        patch.stopall()

    def test_initializes_request_response(self):
        self.patched_unzip.return_value = "<response/>"
        response = RetrieveMessageResponse(self.response_payload())
        self.assertIsInstance(response.request_response, BaseRequestResponse)
        self.assertEqual("<response/>", response.request_response.payload)

    def test_extracts_zipped_response(self):
        self.patched_unzip.return_value = "<response/>"

        response = RetrieveMessageResponse(self.response_payload("Base64EncodedZippedArchive"))
        self.patched_unzip.assert_called_with("Base64EncodedZippedArchive")
        self.assertEqual("<response/>", response.contents)


class SubmitMessageResponseTest(TestCase):
    @staticmethod
    def submit_response_payload():
        return """\
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
    <soap:Body>
        <ns4:submitResponse xmlns:ns4="http://eu.domibus.wsplugin/">
            <messageID>11111111-1111-1111-1111-111111111111</messageID>
        </ns4:submitResponse>
    </soap:Body>
</soap:Envelope>"""

    @staticmethod
    def response_error_payload(code, message):
        return f"""\
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
    <soap:Body>
        <soap:Fault>
            <!-- … -->
            <soap:Detail>
                <ns2:FaultDetail xmlns:ns2="http://eu.domibus.wsplugin/">
                    <code>{code}</code>
                    <message>{message}</message>
                </ns2:FaultDetail>
            </soap:Detail>
        </soap:Fault>
    </soap:Body>
</soap:Envelope>"""

    def test_sets_error_flag_when_error_in_payload(self):
        payload = self.response_error_payload("EBMS:1234", "Some error message")
        response = SubmitMessageResponse(payload)
        self.assertTrue(response.error)
        self.assertEqual("EBMS:1234 - Some error message", response.error_message)

    def test_leaves_error_flag_and_error_message_unset_when_regular_response(self):
        payload = self.submit_response_payload()
        response = SubmitMessageResponse(payload)
        self.assertFalse(response.error)
        self.assertIsNone(response.error_message)

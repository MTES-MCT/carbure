from unittest import TestCase
from unittest.mock import patch

from edelivery.soap.responses import ListPendingMessagesResponse, RetrieveMessageResponse


class ListPendingMessagesResponseTest(TestCase):
    def response_payload(_, message_ids):
        message_ids_to_XML = [f"""<messageID>{id}</messageID>""" for id in message_ids]

        return f"""\
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Body>
    <ns4:listPendingMessagesResponse
      xmlns:xmime="http://www.w3.org/2005/05/xmlmime"
      xmlns:ns5="http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/"
      xmlns:ns4="http://eu.domibus.wsplugin/">
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
    def response_payload(_, attachment_value):
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

    @patch("edelivery.soap.responses.unzip_base64_encoded_stream")
    def test_extracts_zipped_response(self, patched_unzip):
        patched_unzip.return_value = "<response/>"

        response = RetrieveMessageResponse(self.response_payload("Base64EncodedZippedArchive"))
        patched_unzip.assert_called_with("Base64EncodedZippedArchive")
        self.assertEqual("<response/>", response.contents)

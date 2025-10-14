from unittest import TestCase
from unittest.mock import MagicMock, patch

from edelivery.ebms.requests import BaseRequest
from edelivery.soap.actions import ListPendingMessages, RetrieveMessage, SubmitMessage
from edelivery.soap.responses import ListPendingMessagesResponse, RetrieveMessageResponse, SubmitMessageResponse


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


class RetrieveMessageTest(TestCase):
    def test_knows_its_action_name(self):
        action = RetrieveMessage("12345")
        self.assertEqual("retrieveMessage", action.name)

    def test_knows_its_response_class(self):
        action = RetrieveMessage("12345")
        self.assertEqual(RetrieveMessageResponse, action.response_class)

    def test_knows_its_payload(self):
        action = RetrieveMessage("12345")

        expected_payload = """\
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:_1="http://eu.domibus.wsplugin/">
  <soap:Header/>
  <soap:Body>
    <_1:retrieveMessageRequest>
      <messageID>12345</messageID>
    </_1:retrieveMessageRequest>
  </soap:Body>
</soap:Envelope>"""
        self.assertEqual(expected_payload, action.payload())


@patch.dict("os.environ", {"INITIATOR_ACCESS_POINT_ID": "initiator_id", "CARBURE_NTR": "CarbuRe_NTR"})
class SubmitMessageTest(TestCase):
    def test_knows_its_action_name(self):
        request = BaseRequest("12345", "<request/>")
        action = SubmitMessage("responder_id", request)
        self.assertEqual("submitMessage", action.name)

    def test_knows_its_response_class(self):
        request = BaseRequest("12345", "<request/>")
        action = SubmitMessage("responder_id", request)
        self.assertEqual(SubmitMessageResponse, action.response_class)

    @patch.dict("os.environ", {"INITIATOR_ACCESS_POINT_ID": "initiator_id", "CARBURE_NTR": "CarbuRe_NTR"})
    @patch("edelivery.soap.actions.timestamp")
    @patch("edelivery.soap.actions.new_uuid")
    def test_knows_its_payload(self, patched_new_uuid, patched_timestamp):
        patched_new_uuid.return_value = "12345678-1234-1234-1234-1234567890ab"
        patched_timestamp.return_value = "2025-07-15T13:00:00+00:00"
        request = MagicMock()
        request.zipped_encoded.return_value = "abcdef"
        action = SubmitMessage("responder_id", request)

        expected_payload = """\
<soap:Envelope
  xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
  xmlns:ns="http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/"
  xmlns:_1="http://eu.domibus.wsplugin/"
  xmlns:xm="http://www.w3.org/2005/05/xmlmime">

  <soap:Header>
    <eb:Messaging xmlns:eb="http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/">
      <eb:UserMessage>
        <eb:MessageInfo>
          <eb:Timestamp>2025-07-15T13:00:00+00:00</eb:Timestamp>
          <eb:MessageId>12345678-1234-1234-1234-1234567890ab</eb:MessageId>
        </eb:MessageInfo>
        <eb:PartyInfo>
          <eb:From><eb:PartyId type="urn:oasis:names:tc:ebcore:partyid-type:unregistered:UDB">initiator_id</eb:PartyId>
<eb:Role>http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/initiator</eb:Role></eb:From>
          <eb:To><eb:PartyId type="urn:oasis:names:tc:ebcore:partyid-type:unregistered:UDB">responder_id</eb:PartyId>
<eb:Role>http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/responder</eb:Role></eb:To>
        </eb:PartyInfo>
        <eb:CollaborationInfo>
          <eb:Service>https://union-database.ec.europa.eu/e-delivery/services/send</eb:Service>
          <eb:Action>https://union-database.ec.europa.eu/e-delivery/actions/sendRequest</eb:Action>
        </eb:CollaborationInfo>
        <eb:MessageProperties>
          <eb:Property name="originalSender">CarbuRe_NTR</eb:Property>
          <eb:Property name="finalRecipient">EC</eb:Property>
        </eb:MessageProperties>
        <eb:PayloadInfo>
          <eb:PartInfo href="cid:attachment">
            <eb:PartProperties>
              <eb:Property name="MimeType">application/octet-stream</eb:Property>
            </eb:PartProperties>
          </eb:PartInfo>
        </eb:PayloadInfo>
      </eb:UserMessage>
    </eb:Messaging>
  </soap:Header>

  <soap:Body>
    <_1:submitRequest>
      <payload payloadId="cid:attachment" contentType="application/octet-stream">
        <value>abcdef</value>
      </payload>
    </_1:submitRequest>
  </soap:Body>
</soap:Envelope>"""

        self.assertEqual(action.payload(), expected_payload)

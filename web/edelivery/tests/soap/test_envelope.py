from unittest import TestCase
from unittest.mock import MagicMock

from edelivery.soap.envelope import Envelope


class EnvelopeTest(TestCase):
    def test_knows_its_payload(self):
        message = MagicMock()
        message.id = "12345678-1234-1234-1234-1234567890ab"
        message.timestamp = "2025-07-15T13:00:00+00:00"
        message.encoded.return_value = "abcdef"
        message.initiator_id.return_value = "initiator"
        message.initiator_to_XML.return_value = "<MockValue>initiator</MockValue>"
        message.responder_to_XML.return_value = "<MockValue>responder</MockValue>"
        envelope = Envelope(message)
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
          <eb:From><MockValue>initiator</MockValue></eb:From>
          <eb:To><MockValue>responder</MockValue></eb:To>
        </eb:PartyInfo>
        <eb:CollaborationInfo>
          <eb:Service>https://union-database.ec.europa.eu/e-delivery/services/send</eb:Service>
          <eb:Action>https://union-database.ec.europa.eu/e-delivery/actions/sendRequest</eb:Action>
        </eb:CollaborationInfo>
        <eb:MessageProperties>
          <eb:Property name="originalSender">CARBURE</eb:Property>
          <eb:Property name="finalRecipient">EC</eb:Property>
        </eb:MessageProperties>
        <eb:PayloadInfo>
          <eb:PartInfo href="cid:message">
            <eb:PartProperties>
              <eb:Property name="MimeType">text/xml</eb:Property>
            </eb:PartProperties>
          </eb:PartInfo>
        </eb:PayloadInfo>
      </eb:UserMessage>
    </eb:Messaging>
  </soap:Header>

  <soap:Body>
    <_1:submitRequest>
      <payload payloadId="cid:message" contentType="text/xml">
        <value>abcdef</value>
      </payload>
    </_1:submitRequest>
  </soap:Body>
</soap:Envelope>"""

        self.assertEqual(expected_payload, envelope.payload())

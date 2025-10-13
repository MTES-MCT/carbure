from edelivery.adapters.edelivery_adapter import send_SOAP_request
from edelivery.adapters.uuid_generator import new_uuid
from edelivery.soap.responses import ListPendingMessagesResponse, RetrieveMessageResponse, SubmitMessageResponse


class AbstractSoapAction:
    def __init__(self, name, response_class, send_callback):
        self.name = name
        self.response_class = response_class
        self.send_callback = send_callback

    def payload(self):
        raise NotImplementedError("Should be called from a concrete class!")

    def perform(self):
        response = self.send_callback(action=self.name, payload=self.payload())
        return self.response_class(response.text)


class ListPendingMessages(AbstractSoapAction):
    def __init__(self, send_callback=send_SOAP_request):
        super().__init__("listPendingMessages", ListPendingMessagesResponse, send_callback)

    def payload(self):
        return """\
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:_1="http://eu.domibus.wsplugin/">
  <soap:Header/>
  <soap:Body>
    <_1:listPendingMessagesRequest></_1:listPendingMessagesRequest>
  </soap:Body>
</soap:Envelope>"""


class RetrieveMessage(AbstractSoapAction):
    def __init__(self, message_id, send_callback=send_SOAP_request):
        super().__init__("retrieveMessage", RetrieveMessageResponse, send_callback)
        self.message_id = message_id

    def payload(self):
        return f"""\
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:_1="http://eu.domibus.wsplugin/">
  <soap:Header/>
  <soap:Body>
    <_1:retrieveMessageRequest>
      <messageID>{self.message_id}</messageID>
    </_1:retrieveMessageRequest>
  </soap:Body>
</soap:Envelope>"""


class SubmitMessage(AbstractSoapAction):
    def __init__(self, message, send_callback=send_SOAP_request):
        super().__init__("submitMessage", SubmitMessageResponse, send_callback)
        self.message = message
        self.message_id = new_uuid()

    def payload(self):
        return f"""\
<soap:Envelope
  xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
  xmlns:ns="http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/"
  xmlns:_1="http://eu.domibus.wsplugin/"
  xmlns:xm="http://www.w3.org/2005/05/xmlmime">

  <soap:Header>
    <eb:Messaging xmlns:eb="http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/">
      <eb:UserMessage>
        <eb:MessageInfo>
          <eb:Timestamp>{self.message.timestamp}</eb:Timestamp>
          <eb:MessageId>{self.message_id}</eb:MessageId>
        </eb:MessageInfo>
        <eb:PartyInfo>
          <eb:From>{self.message.initiator_to_XML()}</eb:From>
          <eb:To>{self.message.responder_to_XML()}</eb:To>
        </eb:PartyInfo>
        <eb:CollaborationInfo>
          <eb:Service>https://union-database.ec.europa.eu/e-delivery/services/send</eb:Service>
          <eb:Action>https://union-database.ec.europa.eu/e-delivery/actions/sendRequest</eb:Action>
        </eb:CollaborationInfo>
        <eb:MessageProperties>
          <eb:Property name="originalSender">{self.message.original_sender}</eb:Property>
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
        <value>{self.message.zipped_encoded()}</value>
      </payload>
    </_1:submitRequest>
  </soap:Body>
</soap:Envelope>"""

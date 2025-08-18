class Envelope:
    def __init__(self, message):
        self.message = message

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
          <eb:MessageId>{self.message.id}</eb:MessageId>
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

import base64
from os import environ

import requests


def request_headers():
    credentials = bytes(f"""{environ["DOMIBUS_API_LOGIN"]}:{environ["DOMIBUS_API_PASSWORD"]}""", "utf-8")
    encoded_token = base64.b64encode(credentials).decode("utf-8")

    return {
        "Content-Type": "text/xml",
        "Autorization": f"Basic {encoded_token}",
    }


def send_SOAP_request(message):
    payload = f"""\
<soap:Envelope
  xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
  xmlns:ns="http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/"
  xmlns:_1="http://eu.domibus.wsplugin/"
  xmlns:xm="http://www.w3.org/2005/05/xmlmime">

  <soap:Header>
    <eb:Messaging xmlns:eb="http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/">
      <eb:UserMessage>
        <eb:MessageInfo>
          <eb:Timestamp>{message.timestamp}</eb:Timestamp>
          <eb:MessageId>{message.id}</eb:MessageId>
        </eb:MessageInfo>
        <eb:PartyInfo>
          <eb:From>{message.initiator_to_XML()}</eb:From>
          <eb:To>{message.responder_to_XML()}</eb:To>
        </eb:PartyInfo>
        <eb:CollaborationInfo>
          <eb:Service>https://union-database.ec.europa.eu/e-delivery/services/send</eb:Service>
          <eb:Action>https://union-database.ec.europa.eu/e-delivery/actions/sendRequest</eb:Action>
        </eb:CollaborationInfo>
        <eb:MessageProperties>
          <eb:Property name="originalSender">{message.initiator_id()}</eb:Property>
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
        <value>{message.encoded()}</value>
      </payload>
    </_1:submitRequest>
  </soap:Body>
</soap:Envelope>"""

    url = f"""{environ["DOMIBUS_BASE_URL"]}/services/wsplugin/submitMessage"""
    requests.post(url, headers=request_headers(), data=payload)

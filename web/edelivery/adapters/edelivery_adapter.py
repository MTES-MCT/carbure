from os import environ
import xml.etree.ElementTree as ET

import requests

from edelivery.adapters.base64_encoder import encode

def request_headers():
    encoded_credentials = encode(f"""{environ["DOMIBUS_API_LOGIN"]}:{environ["DOMIBUS_API_PASSWORD"]}""")
    return {
        "Authorization": f"""Basic {encoded_credentials}""",
        "Content-Type": "text/xml",
    }


def request_URL(soap_action):
    return f"""{environ["DOMIBUS_BASE_URL"]}/services/wsplugin/{soap_action}"""


def send_SOAP_request(envelope):
    requests.post(request_URL("submitMessage"), headers=request_headers(), data=envelope.payload())

def next_awaiting_message_id():
    soap_request="""\
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:_1="http://eu.domibus.wsplugin/">
  <soap:Header/>
  <soap:Body>
    <_1:listPendingMessagesRequest></_1:listPendingMessagesRequest>
  </soap:Body>
</soap:Envelope>"""

    response = requests.post(request_URL("listPendingMessages"), headers=request_headers(), data=soap_request).text
    parsed_XML = ET.fromstring(response)
    message_id_elements = parsed_XML.findall(".//messageID")
    ids = list(map((lambda e: e.text), message_id_elements))

    if (len(ids) == 0):
        raise LookupError('No awaiting message')

    return ids[0]


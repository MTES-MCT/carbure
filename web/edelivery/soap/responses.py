import xml.etree.ElementTree as ET

from edelivery.adapters.zip_utils import unzip_base64_encoded_stream
from edelivery.ebms.request_responses import BaseRequestResponse


class BaseEdeliveryResponse:
    def __init__(self, text):
        self.text = text
        self.parsed_XML = ET.fromstring(text)


class ListPendingMessagesResponse(BaseEdeliveryResponse):
    def __init__(self, text):
        super().__init__(text)
        self.message_id_elements = self.parsed_XML.findall(".//messageID")

    def next_pending_message_id(self):
        ids = self.pending_message_ids()
        return ids[0]

    def pending_message_ids(self):
        return [e.text for e in self.message_id_elements]

    def pending_message_present(self):
        ids = self.pending_message_ids()
        return len(ids) > 0


class RetrieveMessageResponse(BaseEdeliveryResponse):
    NAMESPACES = {
        "soap": "http://www.w3.org/2003/05/soap-envelope",
        "ws": "http://eu.domibus.wsplugin/",
    }

    def __init__(self, text):
        super().__init__(text)
        self.contents = unzip_base64_encoded_stream(self.attachment_value())
        self.request_response = BaseRequestResponse(self.contents)
        self.request_response_payload = self.request_response.payload

    def attachment_value(self):
        value_element = self.parsed_XML.find("soap:Body/ws:retrieveMessageResponse/payload/value", self.NAMESPACES)
        return value_element.text


class SubmitMessageResponse(BaseEdeliveryResponse):
    def __init__(self, text):
        super().__init__(text)

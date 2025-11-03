import xml.etree.ElementTree as ET

from edelivery.adapters.zip_utils import unzip_base64_encoded_stream
from edelivery.ebms.request_responses import BaseRequestResponse


class BaseEdeliveryResponse:
    NAMESPACES = {
        "soap": "http://www.w3.org/2003/05/soap-envelope",
        "ws": "http://eu.domibus.wsplugin/",
    }

    def __init__(self, text):
        self.text = text
        self.parsed_XML = ET.fromstring(text)

    def find_element(self, path):
        return self.parsed_XML.find(path, self.NAMESPACES)


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
    def __init__(self, text):
        super().__init__(text)
        self.contents = unzip_base64_encoded_stream(self.attachment_value())
        self.request_response = BaseRequestResponse(self.contents)
        self.request_response_payload = self.request_response.payload

    def attachment_value(self):
        value_element = self.find_element("soap:Body/ws:retrieveMessageResponse/payload/value")
        return value_element.text


class SubmitMessageResponse(BaseEdeliveryResponse):
    def __init__(self, text):
        super().__init__(text)
        self.check_for_errors()

    def check_for_errors(self):
        self.error = False
        self.error_message = None

        error_element = self.find_element("soap:Body/soap:Fault")
        if error_element is not None:
            self.error = True
            error_details = self.find_element("soap:Body/soap:Fault/soap:Detail/ws:FaultDetail")
            code = error_details.find("code").text
            message = error_details.find("message").text
            self.error_message = f"{code} - {message}"

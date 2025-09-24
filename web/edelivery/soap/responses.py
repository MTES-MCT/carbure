import xml.etree.ElementTree as ET

from edelivery.adapters.zip_compressor import unzip_base64_encoded_stream


class AbstractEdeliveryResponse:
    def __init__(self, text):
        self.text = text
        self.parsed_XML = ET.fromstring(text)


class ListPendingMessagesResponse(AbstractEdeliveryResponse):
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


class RetrieveMessageResponse(AbstractEdeliveryResponse):
    def __init__(self, text):
        super().__init__(text)
        self.contents = unzip_base64_encoded_stream(self.attachment_value())

    def attachment_value(self):
        namespaces = {"soap": "http://www.w3.org/2003/05/soap-envelope", "ws": "http://eu.domibus.wsplugin/"}
        valueElement = self.parsed_XML.find("soap:Body/ws:retrieveMessageResponse/payload/value", namespaces)
        return valueElement.text


class SubmitMessageResponse(AbstractEdeliveryResponse):
    def __init__(self, text):
        super().__init__(text)

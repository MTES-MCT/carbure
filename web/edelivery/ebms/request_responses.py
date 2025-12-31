import xml.etree.ElementTree as ET


class BaseRequestResponse:
    def __init__(self, payload):
        self.payload = payload
        self.parsed_XML = ET.fromstring(payload)

    def request_id(self):
        response_header_element = self.parsed_XML.find("./RESPONSE_HEADER")
        return response_header_element.attrib["REQUEST_ID"]


class EOGetTransactionResponse(BaseRequestResponse):
    pass

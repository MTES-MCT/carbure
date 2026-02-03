import xml.etree.ElementTree as ET

from edelivery.ebms.error_responses import InvalidRequestErrorResponse, NotFoundErrorResponse, UnknownStatusErrorResponse


class ResponseFactory:
    _ERROR_RESPONSE_CLASSES = {
        "INVALID_REQUEST": InvalidRequestErrorResponse,
        "NOT_FOUND": NotFoundErrorResponse,
    }

    def __init__(self, response_class, payload):
        self.response_class = response_class
        self.payload = payload
        self.parsed_XML = ET.fromstring(payload)

    def response(self):
        response_status = self.udb_response_status()
        status_found = response_status == "FOUND"
        response_class = (
            self.response_class
            if status_found
            else self._ERROR_RESPONSE_CLASSES.get(response_status, UnknownStatusErrorResponse)
        )

        return response_class(self.payload)

    def udb_response_status(self):
        response_header_element = self.parsed_XML.find("./RESPONSE_HEADER")
        return response_header_element.attrib["STATUS"]

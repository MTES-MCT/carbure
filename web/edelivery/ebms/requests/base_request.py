import xml.etree.ElementTree as ET

from edelivery.adapters.uuid_generator import new_uuid
from edelivery.adapters.zip_utils import zip_and_stream_udb_request
from edelivery.ebms.request_responses.base_request_response import BaseRequestResponse


class BaseRequest:
    @staticmethod
    def with_request_id_inserted(request_id, body):
        ET.register_namespace("udb", "http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1")
        xml = ET.fromstring(body)
        request_header_element = ET.Element("REQUEST_HEADER", {"REQUEST_ID": request_id})
        xml.insert(0, request_header_element)
        ET.indent(xml)
        return ET.tostring(xml, encoding="utf-8").decode("utf-8")

    def __init__(self, body, response_class=BaseRequestResponse):
        self.conversation_id = new_uuid()
        self.id = self.conversation_id
        self.body = self.with_request_id_inserted(self.id, body)
        self.response_class = response_class

    def zipped_encoded(self):
        return zip_and_stream_udb_request(self.body)

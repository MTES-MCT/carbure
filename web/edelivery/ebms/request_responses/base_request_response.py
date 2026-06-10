import xml.etree.ElementTree as ET


class BaseRequestResponse:
    def __init__(self, payload):
        self.payload = payload
        self.parsed_XML = ET.fromstring(payload)

    def post_retrieval_action_result(self):
        pass

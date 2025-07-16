from os import environ

from edelivery.adapters.base64_encoder import encode
from edelivery.adapters.clock import timestamp
from edelivery.adapters.uuid_generator import new_uuid
from edelivery.ebms.access_points import Initiator, Responder


class Message:
    def __init__(self, responder_id, body):
        self.id = new_uuid()
        self.initiator = Initiator(environ["INITIATOR_ACCESS_POINT_ID"])
        self.responder = Responder(responder_id)
        self.timestamp = timestamp()
        self.body = body

    def encoded(self):
        return encode(self.body)

    def identifier(self):
        return str(self.id)

    def initiator_id(self):
        return self.initiator.id

    def initiator_to_XML(self):
        return self.initiator.to_XML()

    def responder_to_XML(self):
        return self.responder.to_XML()


class TestMessage(Message):
    def __init__(self):
        super().__init__(environ["INITIATOR_ACCESS_POINT_ID"], "<test>Hello World!</test>")

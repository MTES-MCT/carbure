from os import environ

from edelivery.adapters.base64_encoder import encode
from edelivery.adapters.clock import timestamp
from edelivery.adapters.uuid_generator import new_uuid


class Message:
    def __init__(self, responder_id, body):
        self.id = new_uuid()
        self.timestamp = timestamp()
        self.body = body

    def identifier(self):
        return str(self.id)

    def initiator_id(self):
        return environ["INITIATOR_ACCESS_POINT_ID"]

    def encoded(self):
        return encode(self.body)

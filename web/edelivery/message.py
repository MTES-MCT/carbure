import base64
import datetime
import uuid
from os import environ

from web.edelivery.access_point import Initiator, Responder


class Message:
    def __init__(self, responder, body):
        self.id = uuid.uuid4()
        self.timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.initiator = Initiator(environ["INITIATOR_ACCESS_POINT_ID"])
        self.responder = Responder(responder)
        self.body = body

    def encoded(self):
        return base64.b64encode(bytes(self.body, "utf-8")).decode("utf-8")

    def initiator_id(self):
        return self.initiator.id

    def initiator_to_XML(self):
        return self.initiator.to_XML()

    def responder_to_XML(self):
        return self.responder.to_XML()


class TestMessage(Message):
    def __init__(self):
        super().__init__(environ["INITIATOR_ACCESS_POINT_ID"], "<test>Hello World</test>")

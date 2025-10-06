import asyncio
import redis
import time

from os import environ

from edelivery.adapters.edelivery_adapter import send_SOAP_request
from edelivery.soap.actions import ListPendingMessages, RetrieveMessage, SubmitMessage


REDIS_CHANNEL = "eDelivery messages"

class EdeliveryListener():
    def __init__(self, send_callback=send_SOAP_request):
        self.send_callback = send_callback
        self.subscribers = {}
        self.redis = redis.from_url(environ["REDIS_URL"])

    def listen(self):
        while True:
            print("New attempt…")
            r = ListPendingMessages(self.send_callback).perform()
            if r.pending_message_present():
                print("New message pending!")
                i = r.next_pending_message_id()
                rr = RetrieveMessage(i, self.send_callback).perform().request_response.payload
                self.redis.publish(REDIS_CHANNEL, rr)
            time.sleep(1)


class Requester:
    def __init__(self, request):
        self.request = request
        redis_client = redis.from_url(environ["REDIS_URL"])
        self.redis_channel = redis_client.pubsub(ignore_subscribe_messages=True)

    def response(self):
        self.redis_channel.subscribe(REDIS_CHANNEL)
        SubmitMessage(self.request).perform()
        return self.udb_response()

    def udb_response(self):
        result = None
        delay = 0.01
        i = 0

        while i < 15 / delay:
            i += 1
            message = self.redis_channel.get_message()
            if message: result = message["data"]
            time.sleep(0.01)

        return result

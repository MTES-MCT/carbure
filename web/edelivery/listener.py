import asyncio

from edelivery.adapters.edelivery_adapter import send_SOAP_request
from edelivery.soap.actions import ListPendingMessages, RetrieveMessage, SubmitMessage


class EdeliveryListener():
    def __init__(self, send_callback=send_SOAP_request):
        self.send_callback = send_callback
        self.subscribers = {}

    def start(self):
        asyncio.create_task(self.listen())

    def subscribe(self, requester, request_id):
        self.subscribers[request_id] = requester

    def trigger_message_received(self, request_response):
        request_id = request_response.request_id()
        print(request_id)
        if request_id in self.subscribers.keys():
            requester = self.subscribers[request_id]
            requester.response_received(request_response)

    def unsubscribe(self, request_id):
        if request_id in self.subscribers.keys():
            self.subscribers.pop(request_id)

    async def listen(self):
        while True:
            r = ListPendingMessages(self.send_callback).perform()
            if r.pending_message_present():
                i = r.next_pending_message_id()
                rr = RetrieveMessage(i, self.send_callback).perform().request_response
                self.trigger_message_received(rr)
            await asyncio.sleep(1)


class Requester:
    def __init__(self, request, el):
        self.request = request
        self.el = el
        self.request_response = None

    def response_received(self, request_response):
        self.request_response = request_response

    async def response(self):
        self.el.subscribe(self, "ABC-1234567890")
        SubmitMessage(self.request).perform()
        async with asyncio.timeout(10):
            return await self.udb_response()

    async def udb_response(self):
        while True:
            if self.request_response != None:
                return self.request_response
            await asyncio.sleep(1)

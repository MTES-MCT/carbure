from os import environ
from time import sleep

from edelivery.adapters.pub_sub_adapter import PubSubAdapter
from edelivery.soap.actions import SubmitMessage


class Requester:
    def __init__(self, request, delay_between_retries=0.1, timeout=10):
        self.request = request
        self.delay_between_retries = delay_between_retries
        self.timeout = timeout
        self.pub_sub_adapter = PubSubAdapter()

    def response(self):
        def wait_for_udb_response():
            tried = 0

            while tried < self.timeout / self.delay_between_retries:
                tried += 1
                message = self.pub_sub_adapter.next_message()
                if message is not None:
                    candidate = self.request.response_class(message)
                    if candidate.request_id() == self.request.id:
                        return candidate
                sleep(self.delay_between_retries)

            raise TimeoutError()

        try:
            self.pub_sub_adapter.subscribe()
            SubmitMessage(environ["UDB_ACCESS_POINT_ID"], self.request).perform()

            return wait_for_udb_response()

        finally:
            self.pub_sub_adapter.unsubscribe()

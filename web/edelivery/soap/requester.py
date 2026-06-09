import json
from os import environ
from time import sleep

from edelivery.adapters.pub_sub_adapter import PubSubAdapter
from edelivery.ebms.response_factory import ResponseFactory
from edelivery.soap.actions import SubmitMessage


class Requester:
    def __init__(self, request, delay_between_retries=0.1, timeout=10):
        self.request = request
        self.delay_between_retries = delay_between_retries
        self.timeout = timeout
        self.pub_sub_adapter = PubSubAdapter()

    def do_request(self):
        def wait_for_udb_response():
            tried = 0

            while tried < self.timeout / self.delay_between_retries:
                tried += 1
                message = self.pub_sub_adapter.next_message()
                if message is not None:
                    message_as_json = json.loads(message)
                    conversation_id = message_as_json["conversation_id"]
                    if conversation_id == self.request.conversation_id:
                        payload = message_as_json["payload"]
                        factory = ResponseFactory(self.request.response_class, payload)
                        return factory.response()
                sleep(self.delay_between_retries)

            raise TimeoutError()

        try:
            self.pub_sub_adapter.subscribe()
            SubmitMessage(environ["UDB_ACCESS_POINT_ID"], self.request).perform()

            response = wait_for_udb_response()
            return response.post_retrieval_action_result()

        finally:
            self.pub_sub_adapter.unsubscribe()

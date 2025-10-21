from time import sleep

from edelivery.adapters.pub_sub_adapter import PubSubAdapter
from edelivery.soap.actions import ListPendingMessages, RetrieveMessage


class Listener:
    def __init__(self):
        self.pub_sub_adapter = PubSubAdapter()

    def poll_once(self):
        list = ListPendingMessages().perform()
        if list.pending_message_present():
            id = list.next_pending_message_id()
            payload = RetrieveMessage(id).perform().request_response_payload
            self.pub_sub_adapter.publish(payload)

    def start(self):
        while True:
            self.poll_once()
            sleep(1)

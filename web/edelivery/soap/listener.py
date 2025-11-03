from os import environ
from time import sleep

from edelivery.adapters.pub_sub_adapter import PubSubAdapter
from edelivery.soap.actions import ListPendingMessages, RetrieveMessage


class Listener:
    START_SERVICE_COMMAND = "start_listener"
    STOP_SERVICE_COMMAND = "stop_listener"

    @staticmethod
    def send_stop_signal():
        p = PubSubAdapter()
        p.service(Listener.STOP_SERVICE_COMMAND)

    @staticmethod
    def send_start_signal():
        p = PubSubAdapter()
        p.service(Listener.START_SERVICE_COMMAND)

    def __init__(self):
        self.pub_sub_adapter = PubSubAdapter()
        self.pub_sub_adapter.subscribeToServiceChannel()
        self.started = False

    def poll_once(self):
        if "WITH_EDELIVERY" not in environ.keys() or environ["WITH_EDELIVERY"] != "True":
            return

        list = ListPendingMessages().perform()
        if list.pending_message_present():
            id = list.next_pending_message_id()
            payload = RetrieveMessage(id).perform().request_response_payload
            self.pub_sub_adapter.publish(payload)

    def start(self):
        self.started = True

        while True:
            message = self.pub_sub_adapter.next_message()
            if message == Listener.STOP_SERVICE_COMMAND:
                self.started = False

            if message == Listener.START_SERVICE_COMMAND:
                self.started = True

            if self.started:
                self.poll_once()

            sleep(1)

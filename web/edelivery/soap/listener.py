import json
from os import environ
from time import sleep

from adapters.logger import log_exception
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
            response = RetrieveMessage(id).perform()
            conversation_id = response.conversation_id()
            payload = response.request_response_payload
            message = json.dumps({"conversation_id": conversation_id, "payload": payload})
            self.pub_sub_adapter.publish(message)

    def start(self):
        self.started = True

        while True:
            try:
                message = self.pub_sub_adapter.next_message()
                if message == Listener.STOP_SERVICE_COMMAND:
                    self.started = False

                if message == Listener.START_SERVICE_COMMAND:
                    self.started = True

                if self.started:
                    self.poll_once()

            except Exception as e:
                log_exception(e)

            finally:
                sleep(1)

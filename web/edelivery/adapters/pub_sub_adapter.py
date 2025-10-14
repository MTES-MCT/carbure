from os import environ

import redis


class PubSubAdapter:
    REDIS_CHANNEL = "eDelivery messages"

    def __init__(self):
        redis_client = redis.from_url(environ["REDIS_URL"])
        self.pubsub = redis_client.pubsub(ignore_subscribe_messages=True)

    def next_message(self):
        self.pubsub.get_message()

    def subscribe(self):
        self.pubsub.subscribe(self.REDIS_CHANNEL)

    def unsubscribe(self):
        self.pubsub.unsubscribe(self.REDIS_CHANNEL)

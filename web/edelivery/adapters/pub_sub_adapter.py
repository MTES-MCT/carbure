from os import environ

import redis


class PubSubAdapter:
    REDIS_CHANNEL = "eDelivery messages"

    def __init__(self):
        self.redis_client = redis.from_url(environ["REDIS_URL"])
        self.pubsub = self.redis_client.pubsub(ignore_subscribe_messages=True)

    def next_message(self):
        return self.pubsub.get_message()

    def publish(self, message):
        return self.redis_client.publish(self.REDIS_CHANNEL, message)

    def subscribe(self):
        return self.pubsub.subscribe(self.REDIS_CHANNEL)

    def unsubscribe(self):
        return self.pubsub.unsubscribe(self.REDIS_CHANNEL)

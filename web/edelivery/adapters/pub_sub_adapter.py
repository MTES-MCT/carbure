from os import environ

import redis


class PubSubAdapter:
    REDIS_RESPONSES_CHANNEL = "eDelivery responses"
    REDIS_SERVICE_CHANNEL = "eDelivery service"

    def __init__(self):
        self.redis_client = redis.from_url(environ["REDIS_URL"])
        self.pubsub = self.redis_client.pubsub(ignore_subscribe_messages=True)

    def next_message(self):
        message = self.pubsub.get_message()
        return message and message["data"].decode("utf-8")

    def publish(self, message):
        return self.redis_client.publish(self.REDIS_RESPONSES_CHANNEL, message)

    def service(self, message):
        return self.redis_client.publish(self.REDIS_SERVICE_CHANNEL, message)

    def subscribe(self):
        return self.pubsub.subscribe(self.REDIS_RESPONSES_CHANNEL)

    def subscribeToServiceChannel(self):
        return self.pubsub.subscribe(self.REDIS_SERVICE_CHANNEL)

    def unsubscribe(self):
        return self.pubsub.unsubscribe(self.REDIS_RESPONSES_CHANNEL)

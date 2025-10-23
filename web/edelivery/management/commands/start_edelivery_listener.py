from django.core.management.base import BaseCommand

from edelivery.soap.listener import Listener


class Command(BaseCommand):
    help = "Start eDelivery listener (will poll eDelivery endpoint every second)"

    def handle(self, *args, **options):
        self.stdout.write("Launching eDelivery listener…")
        Listener().start()

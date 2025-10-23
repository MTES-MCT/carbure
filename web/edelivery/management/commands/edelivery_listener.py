from django.core.management.base import BaseCommand

from edelivery.soap.listener import Listener


class Command(BaseCommand):
    help = "Pilot eDelivery listener."

    def add_arguments(self, parser):
        parser.add_argument(
            "--launch",
            action="store_true",
            help="launch the listener (will poll eDelivery endpoint every second, should be called at startup only)",
        )
        parser.add_argument("--stop", action="store_true", help="stop the listener")
        parser.add_argument("--restart", action="store_true", help="restart the listener")

    def handle(self, *args, **options):
        if options["launch"]:
            self.stdout.write("Launching eDelivery listener…")
            Listener().start()

        if options["stop"]:
            self.stdout.write("Stopping eDelivery listener…")
            Listener.send_stop_signal()
            return

        if options["restart"]:
            self.stdout.write("Restarting eDelivery listener…")
            Listener.send_start_signal()
            return

        self.stderr.write("Missing command! Should either --launch, --stop or --restart")

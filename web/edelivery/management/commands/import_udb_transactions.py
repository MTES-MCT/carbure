from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from edelivery.ebms.requests import EOGetTransactionRequest
from edelivery.soap.requester import Requester


class Command(BaseCommand):
    help = "Import UDB transactions recently created."

    def add_arguments(self, parser):
        parser.add_argument(
            "--minutes_count",
            type=int,
            default=10,
            help="import transactions created during the past minutes (defaulting to 10 minutes)",
        )

    def handle(self, *args, **options):
        date = datetime.now() - timedelta(minutes=options["minutes_count"])
        request = EOGetTransactionRequest(from_creation_date=date)
        requester = Requester(request, timeout=30)
        result = requester.do_request()
        self.stdout.write(str(result))

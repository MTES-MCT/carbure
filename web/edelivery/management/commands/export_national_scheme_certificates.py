from django.core.management.base import BaseCommand

from core.models import EntityCertificate
from edelivery.ebms.requests.add_update_certificate_request import AddUpdateCertificateRequest
from edelivery.soap.requester import Requester


class Command(BaseCommand):
    help = "Export national scheme certificates to UDB"

    def add_arguments(self, parser):
        parser.add_argument(
            "--entity_name",
            type=str,
            required=True,
            help="export certificate for given entity",
        )

    def handle(self, *args, **options):
        ec = EntityCertificate.objects.get(entity__name=options["entity_name"])
        r_add_certificate = AddUpdateCertificateRequest(ec)
        rq = Requester(r_add_certificate, timeout=30)
        result = rq.do_request()
        self.stdout.write(str(result))

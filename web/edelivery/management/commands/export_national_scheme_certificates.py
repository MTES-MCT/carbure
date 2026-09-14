from django.core.management.base import BaseCommand

from core.models.certificate import EntityCertificate
from core.models.entity import Entity
from edelivery.ebms.requests.add_update_certificate_request import AddUpdateCertificateRequest
from edelivery.ebms.requests.get_organisation_by_id_request import GetOrganisationByIDRequest
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
        def entity_not_in_udb(entity):
            self.stdout.write(f"Checking if entity '{entity.name}' present in UDB…")
            request = GetOrganisationByIDRequest(entity.ntr_id())
            requester = Requester(request, timeout=30)
            result = requester.do_request()
            return "error" in result

        entity = Entity.objects.get(name=options["entity_name"])
        if entity_not_in_udb(entity):
            self.stderr.write(f"Error: Entity '{entity.name}' needs to be present in UDB.")
            exit(1)

        ec = EntityCertificate.objects.get(entity=entity)
        request = AddUpdateCertificateRequest(ec)
        requester = Requester(request, timeout=30)
        result = requester.do_request()
        self.stdout.write(str(result))

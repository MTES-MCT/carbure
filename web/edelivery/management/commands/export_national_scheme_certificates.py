from django.core.management.base import BaseCommand

from core.models.certificate import EntityCertificate
from core.models.entity import Entity
from edelivery.ebms.requests.add_organisation_request import AddOrganisationRequest
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

        def export_entity(entity):
            self.stdout.write("Creating entity in UDB…")
            request = AddOrganisationRequest(entity)
            requester = Requester(request, timeout=30)
            requester.do_request()

        def export_certificates(entity):
            entity_certificates = EntityCertificate.objects.filter(entity=entity)
            entity_certificate_ids = ", ".join([f"'{ec.certificate.certificate_id}'" for ec in entity_certificates])
            self.stdout.write(
                f"Exporting certificate{'s' if len(entity_certificates) > 1 else ''} {entity_certificate_ids}…"
            )
            request = AddUpdateCertificateRequest(*entity_certificates)
            requester = Requester(request, timeout=30)
            result = requester.do_request()
            return result

        entity = Entity.objects.get(name=options["entity_name"])
        if entity_not_in_udb(entity):
            export_entity(entity)

        result = export_certificates(entity)
        self.stdout.write(str(result))

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

        parser.add_argument(
            "--dry_run",
            action="store_true",
            help="Dry run the export: do checks and print what UDB request would be sent",
        )

    def handle(self, *args, **options):
        def entity_not_in_udb(entity, dry_run):
            if dry_run:
                self.stdout.write(f"Would check if '{entity.name}' present in UDB… (assuming not)")
                return True

            self.stdout.write(f"Checking if entity '{entity.name}' present in UDB…")
            request = GetOrganisationByIDRequest(entity.ntr_id())
            requester = Requester(request, timeout=30)
            result = requester.do_request()
            return "error" in result

        def export_entity(entity, dry_run):
            if dry_run:
                self.stdout.write("Would create entity in UDB…")
                return

            self.stdout.write("Creating entity in UDB…")
            request = AddOrganisationRequest(entity)
            requester = Requester(request, timeout=30)
            requester.do_request()

        def export_certificates(entity, dry_run):
            entity_certificates = EntityCertificate.objects.filter(entity=entity)
            entity_certificate_ids = ", ".join([f"'{ec.certificate.certificate_id}'" for ec in entity_certificates])

            if dry_run:
                self.stdout.write(
                    f"Would export certificate{'s' if len(entity_certificates) > 1 else ''} {entity_certificate_ids}…"
                )

            request = AddUpdateCertificateRequest(*entity_certificates)
            if dry_run:
                self.stdout.write(f"""\
Would send UDB request with body being:
{request.body}
…""")
                return {"result": "Got to the end of the dry run"}

            self.stdout.write(
                f"Exporting certificate{'s' if len(entity_certificates) > 1 else ''} {entity_certificate_ids}…"
            )
            requester = Requester(request, timeout=30)
            result = requester.do_request()
            return result

        dry_run = options["dry_run"]
        entity = Entity.objects.get(name=options["entity_name"])
        if entity_not_in_udb(entity, dry_run):
            export_entity(entity, dry_run)

        result = export_certificates(entity, dry_run)
        self.stdout.write(str(result))

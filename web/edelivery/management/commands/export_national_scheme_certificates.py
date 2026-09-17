from django.core.management.base import BaseCommand

from core.models.certificate import EntityCertificate, GenericCertificate
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
            help="export certificate for given entity",
        )

        parser.add_argument(
            "--dry_run",
            action="store_true",
            help="Dry run the export: do checks and print what UDB request would be sent",
        )

        parser.add_argument(
            "--all",
            action="store_true",
            help="Export all NS certificates with status 'VALID'",
        )

    def handle(self, *args, **options):
        def carbure_entities(options):
            export_all_certificates = options["all"]
            entity_name = options["entity_name"]

            if export_all_certificates:
                entity_certificates = EntityCertificate.objects.filter(
                    certificate__certificate_type=GenericCertificate.SYSTEME_NATIONAL,
                    certificate__status=GenericCertificate.VALID,
                )
                return [ec.entity for ec in entity_certificates]

            if not entity_name:
                self.stderr.write("Missing parameter: if --all option not set, an entity name should be provided")
                exit(1)

            entities = Entity.objects.filter(name=entity_name)
            if not entities:
                self.stderr.write(f"Value error: Entity `{entity_name}` not found in CarbuRe")
                exit(1)

            return entities

        def find_entities_not_in_udb(entities, dry_run):
            entity_names = ", ".join([f"'{e.name}'" for e in entities])
            ntr_ids = [e.ntr_id() for e in entities]

            if dry_run:
                self.stdout.write(
                    f"Would check if entit{'ies' if len(entities) > 1 else "y"}"
                    f"{entity_names} present in UDB… (assuming not)"
                )
                return entities

            self.stdout.write(f"Checking if entit{'ies' if len(entities) > 1 else "y"} {entity_names} present in UDB…")
            request = GetOrganisationByIDRequest(*ntr_ids)
            requester = Requester(request, timeout=70)
            result = requester.do_request()

            found_organisations_key = "found_organisations"
            if found_organisations_key not in result:
                return entities

            return [e for e in entities if e.ntr_id() not in result[found_organisations_key]]

        def export_entities(entities, dry_run):
            entity_names = ", ".join([f"'{e.name}'" for e in entities])
            if dry_run:
                self.stdout.write(f"Would create entit{'ies' if len(entities) > 1 else "y"} {entity_names} in UDB…")
                return

            self.stdout.write(f"Creating entit{'ies' if len(entities) > 1 else "y"} {entity_names} in UDB…")
            request = AddOrganisationRequest(*entities)
            requester = Requester(request, timeout=70)
            requester.do_request()

        def export_certificates(entities, dry_run):
            entity_certificates = EntityCertificate.objects.filter(
                entity__in=entities,
                certificate__certificate_type=GenericCertificate.SYSTEME_NATIONAL,
                certificate__status=GenericCertificate.VALID,
            )
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
            requester = Requester(request, timeout=70)
            result = requester.do_request()
            return result

        dry_run = options["dry_run"]

        entities = carbure_entities(options)
        entities_not_in_udb = find_entities_not_in_udb(entities, dry_run)
        if entities_not_in_udb:
            export_entities(entities_not_in_udb, dry_run)
        result = export_certificates(entities, dry_run)
        self.stdout.write(str(result))

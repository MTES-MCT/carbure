from django.core.management.base import BaseCommand

from core.models.certificate import GenericCertificate
from core.models.entity import Entity
from core.models.entity_certificate import EntityCertificate
from edelivery.ebms.requests.add_organisation_request import AddOrganisationRequest
from edelivery.ebms.requests.add_update_certificate_request import AddUpdateCertificateRequest
from edelivery.ebms.requests.get_organisation_by_id_request import GetOrganisationByIDRequest
from edelivery.soap.requester import Requester


def carbure_entities(fetch_all=False, entity_name=None):
    if fetch_all:
        entities = Entity.all_currently_certified_under_national_scheme()
        if not entities:
            raise RuntimeError("No entity found with currently valid national scheme certificate")
        return entities

    if not entity_name:
        raise ValueError("Missing parameter: if --all option not set, an entity name should be provided")

    entities = Entity.objects.filter(name=entity_name)
    if not entities:
        raise ValueError(f"Value error: Entity '{entity_name}' not found in CarbuRe")
    return entities


def certificate_ids(entity_certificates):
    if not entity_certificates:
        return "no certificate"

    ids = ", ".join([f"'{ec.certificate.certificate_id}'" for ec in entity_certificates])
    certificates_label = "certificates" if len(entity_certificates) > 1 else "certificate"
    return f"{certificates_label} {ids}"


def entity_names(entities):
    if not entities:
        return "no entity"

    names = ", ".join([f"'{e.name}'" for e in entities])
    entities_label = "entities" if len(entities) > 1 else "entity"
    return f"{entities_label} {names}"


def export_entities(entities):
    if not entities:
        return

    request = AddOrganisationRequest(*entities)
    requester = Requester(request, timeout=70)
    requester.do_request()


def find_entities_not_in_udb(entities):
    ntr_ids = [e.ntr_id() for e in entities]
    request = GetOrganisationByIDRequest(*ntr_ids)
    requester = Requester(request, timeout=70)
    result = requester.do_request()

    found_organisations = result.get("found_organisations", [])
    return [e for e in entities if e.ntr_id() not in found_organisations]


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
        def export_certificates(entities, dry_run):
            entity_certificates = EntityCertificate.objects.filter(
                entity__in=entities,
                certificate__certificate_type=GenericCertificate.SYSTEME_NATIONAL,
                certificate__status=GenericCertificate.VALID,
            )

            if dry_run:
                self.stdout.write(f"Would export {certificate_ids(entity_certificates)}…")

            request = AddUpdateCertificateRequest(*entity_certificates)
            if dry_run:
                self.stdout.write(f"""\
Would send UDB request with body being:
{request.body}
…""")
                return {"result": "Got to the end of the dry run"}

            self.stdout.write(f"Exporting {certificate_ids(entity_certificates)}…")
            requester = Requester(request, timeout=70)
            result = requester.do_request()
            return result

        dry_run = options["dry_run"]
        fetch_all = options["all"]
        entity_name = options["entity_name"]

        entities = carbure_entities(fetch_all=fetch_all, entity_name=entity_name)
        if dry_run:
            self.stdout.write(f"Would check if {entity_names(entities)} present in UDB… (assuming not)")
            self.stdout.write(f"Would create {entity_names(entities)} in UDB…")
        else:
            self.stdout.write(f"Checking if {entity_names(entities)} present in UDB…")
            entities_not_in_udb = find_entities_not_in_udb(entities)
            self.stdout.write(f"Creating {entity_names(entities)} in UDB…")
            export_entities(entities_not_in_udb)

        result = export_certificates(entities, dry_run)
        self.stdout.write(str(result))

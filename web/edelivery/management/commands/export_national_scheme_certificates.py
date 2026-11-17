from functools import reduce

from django.core.management.base import BaseCommand

from core.models.entity import Entity
from core.models.entity_certificate import EntityCertificate
from edelivery.ebms.requests.add_organisation_request import AddOrganisationRequest
from edelivery.ebms.requests.add_update_certificate_request import AddUpdateCertificateRequest
from edelivery.ebms.requests.get_organisation_by_id_request import GetOrganisationByIDRequest
from edelivery.soap.requester import Requester


def carbure_entities(fetch_all=False, entity_name=None):
    def check_validity(acc, entity):
        try:
            entity.ntr_id()
            acc[0].append(entity)
        except Exception as e:
            acc[1].append(e.args[0])

        return acc

    if fetch_all:
        fetched_entities = Entity.all_currently_certified_under_national_scheme()
        (entities, errors) = reduce(check_validity, fetched_entities, ([], []))
        if not entities:
            error_message = (
                f"No valid entity found: {'; '.join(errors)}"
                if errors
                else "No entity found with currently valid national scheme certificate"
            )
            raise RuntimeError(error_message)
        return (entities, errors)

    if not entity_name:
        raise ValueError("Missing parameter: if --all option not set, an entity name should be provided")

    fetched_entities = Entity.objects.filter(name=entity_name)
    (entities, errors) = reduce(check_validity, fetched_entities, ([], []))
    if not entities:
        errors = errors or [f"Entity '{entity_name}' not found in CarbuRe"]
        raise RuntimeError(f"No entity to process: {'; '.join(errors)}")
    return (entities, [])


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


def export_certificates(entities):
    entity_certificates = EntityCertificate.all_for_entities_with_valid_national_scheme_certificate(entities)
    if not entity_certificates:
        raise RuntimeError(f"No valid NS certificate found for {entity_names(entities)}")

    request = AddUpdateCertificateRequest(*entity_certificates)
    requester = Requester(request, timeout=70)
    return requester.do_request()


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
        dry_run = options["dry_run"]
        fetch_all = options["all"]
        entity_name = options["entity_name"]

        (entities, errors) = carbure_entities(fetch_all=fetch_all, entity_name=entity_name)
        entity_certificates = EntityCertificate.all_for_entities_with_valid_national_scheme_certificate(entities)
        request = AddUpdateCertificateRequest(*entity_certificates)

        if dry_run:
            self.stdout.write(f"Would check if {entity_names(entities)} present in UDB… (assuming not)")
            self.stdout.write(f"Would create {entity_names(entities)} in UDB…")
            self.stdout.write(f"Would export {certificate_ids(entity_certificates)}…")
            if entity_certificates:
                self.stdout.write(f"""\
Would send UDB request with body being:
{request.body}
…""")
            self.stdout.write("End of dry run")
            exit(0)

        self.stdout.write(f"Checking if {entity_names(entities)} present in UDB…")
        entities_not_in_udb = find_entities_not_in_udb(entities)

        self.stdout.write(f"Creating {entity_names(entities)} in UDB…")
        export_entities(entities_not_in_udb)

        self.stdout.write(f"Exporting {certificate_ids(entity_certificates)}…")
        result = export_certificates(entities)
        self.stdout.write(str(result))

        if errors:
            self.stderr.write(f"Errors encountered: {errors}")

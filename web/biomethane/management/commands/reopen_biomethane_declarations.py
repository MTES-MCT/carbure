import argparse

from django.core.management.base import BaseCommand

from biomethane.models import BiomethaneAnnualDeclaration
from biomethane.services.annual_declaration.notification import (
    get_reopen_notification_recipients,
    reopen_declaration,
)
from core.models import Entity


def parse_entity_ids(value):
    try:
        entity_ids = [int(entity_id.strip()) for entity_id in value.split(",") if entity_id.strip()]
    except ValueError as error:
        raise argparse.ArgumentTypeError("entity-ids must be a comma-separated list of integers") from error
    if not entity_ids:
        raise argparse.ArgumentTypeError("entity-ids must contain at least one id")
    return entity_ids


class Command(BaseCommand):
    help = """
    Reopen biomethane annual declarations for the given entities and year, then email their users.

    Usage:
        python web/manage.py reopen_biomethane_declarations --year 2025 --entity-ids 1,2,3 --dry-run=true
        python web/manage.py reopen_biomethane_declarations --year 2025 --entity-ids 1,2,3 --dry-run=false
    """

    def add_arguments(self, parser):
        parser.add_argument("--year", type=int, required=True, help="Declaration year to reopen")
        parser.add_argument(
            "--entity-ids",
            type=parse_entity_ids,
            required=True,
            help="Comma-separated producer entity ids whose declaration should be reopened",
        )
        parser.add_argument(
            "--dry-run",
            choices=["true", "false"],
            default="true",
            help="Simulate the reopening and the emails without writing or sending",
        )

    def handle(self, *args, **options):
        year = options["year"]
        dry_run = options["dry_run"] == "true"
        entity_ids = options["entity_ids"]
        if isinstance(entity_ids, str):
            entity_ids = parse_entity_ids(entity_ids)

        for entity_id in entity_ids:
            self._reopen_declaration(entity_id, year, dry_run)

    def _reopen_declaration(self, entity_id, year, dry_run):
        try:
            entity = Entity.objects.get(pk=entity_id)
        except Entity.DoesNotExist:
            self.stdout.write(self.style.WARNING(f"Entity {entity_id} does not exist. Skipping."))
            return

        declaration = BiomethaneAnnualDeclaration.objects.filter(producer=entity, year=year).first()
        if declaration is None:
            self.stdout.write(self.style.WARNING(f"No declaration for entity {entity_id} in {year}. Skipping."))
            return

        if dry_run:
            recipients = get_reopen_notification_recipients(entity)
            self.stdout.write(
                f"[dry-run] Would reopen declaration {year} for entity {entity_id} and email {recipients or 'nobody'}."
            )
            return

        recipients = reopen_declaration(declaration)
        if not recipients:
            self.stdout.write(self.style.WARNING(f"Declaration {year} reopened for entity {entity_id}, no recipients."))
            return

        self.stdout.write(self.style.SUCCESS(f"Declaration {year} reopened for entity {entity_id}, email sent."))

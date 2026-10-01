import argparse

from django.conf import settings
from django.core.management.base import BaseCommand

from biomethane.models import BiomethaneAnnualDeclaration
from core.helpers import send_mail
from core.models import Entity, UserRights

EMAIL_SUBJECT = "Carbure - Réouverture de votre déclaration {year}"
EMAIL_BODY = """Bonjour,
Nous vous informons que votre déclaration {year} dans CarbuRe a été réouverte.
Nous vous invitons à vous connecter via le lien ci-dessous afin de la finaliser.
https://carbure.beta.gouv.fr/
L'équipe CarbuRe
"""


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
        entity_ids = parse_entity_ids(entity_ids)

        for entity_id in entity_ids:
            self._reopen_declaration(entity_id, year, dry_run)

    def _reopen_declaration(self, entity_id, year, dry_run):
        try:
            entity = Entity.objects.get(pk=entity_id)
        except Entity.DoesNotExist:
            self.stdout.write(self.style.WARNING(f"Entity {entity_id} does not exist. Skipping."))
            return

        declaration = BiomethaneAnnualDeclaration.objects.filter(producer=entity, year=year)
        if not declaration.exists():
            self.stdout.write(self.style.WARNING(f"No declaration for entity {entity_id} in {year}. Skipping."))
            return

        recipients = list(
            entity.get_users_emails(role__in=[UserRights.ADMIN, UserRights.RW]).order_by("user__email").distinct()
        )
        if dry_run:
            self.stdout.write(
                f"[dry-run] Would reopen declaration {year} for entity {entity_id} and email {recipients or 'nobody'}."
            )
            return

        declaration.update(is_open=True, status=BiomethaneAnnualDeclaration.IN_PROGRESS)
        if not recipients:
            self.stdout.write(self.style.WARNING(f"Declaration {year} reopened for entity {entity_id}, no recipients."))
            return

        send_mail(
            request=None,
            subject=EMAIL_SUBJECT.format(year=year),
            message=EMAIL_BODY.format(year=year),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
        )
        self.stdout.write(self.style.SUCCESS(f"Declaration {year} reopened for entity {entity_id}, email sent."))

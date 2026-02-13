from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db.models import Count, Q

from core.models import CarbureLot, Entity
from saf.models.constants import SAF_BIOFUEL_TYPES
from saf.models.saf_ticket_source import SafTicketSource


class Command(BaseCommand):
    # command: python web/manage.py delete_ticket_sources_not_eligible_for_saf
    help = "Locate any ticket source that was created from a non-eligible CarbureLot, and delete them if not already used"

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            help="Actually delete the ticket sources from DB",
            action="store_true",
            default=False,
        )

    def handle(self, *args, **options):
        call_command("propagate_saf_origin")

        saf_filter = Q(biofuel__code__in=SAF_BIOFUEL_TYPES)

        owner_filter = (
            Q(added_by__entity_type=Entity.OPERATOR, added_by__has_saf=True)  #
            | Q(added_by__entity_type=Entity.SAF_TRADER)
        )

        origin_lot_filter = Q(
            origin_lot__lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN],
            origin_lot__delivery_type__in=[CarbureLot.BLENDING, CarbureLot.DIRECT, CarbureLot.UNKNOWN],
        )

        ticket_sources = (
            SafTicketSource.objects.exclude(saf_filter & owner_filter & origin_lot_filter)
            .annotate(created_tickets=Count("saf_tickets"))
            .filter(created_tickets=0)
        )

        print(f"> Preparing to delete {ticket_sources.count()} SAF volumes...")

        if options["apply"]:
            ticket_sources.delete()

        print("> Done")

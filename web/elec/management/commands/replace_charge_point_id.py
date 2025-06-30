import logging

from django.core.management.base import BaseCommand

from elec.services.replace_charge_point_id import replace_charge_point_id

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Replace old charge point IDs with newer versions from an Excel mapping file."

    def add_arguments(self, parser):
        parser.add_argument(
            "--cpo",
            type=str,
            required=True,
            help="Partial name to filter CPOs",
        )
        parser.add_argument(
            "--file",
            type=str,
            required=True,
            help="Path to the Excel file containing two columns: old_id, new_id.",
        )
        parser.add_argument(
            "--apply",
            type=bool,
            default=False,
            help="Save the results in the database",
        )

    def handle(self, *args, **options):
        cpo = options["cpo"]
        file = options["file"]
        apply = options["apply"]

        updated, deleted, not_found = replace_charge_point_id(cpo, file, apply)

        logger.info(f"> Successfully updated {len(updated)} PDCs")

        if deleted:
            logger.warning(f"> {len(deleted)} PDCs marked as deleted")
        if not_found:
            logger.warning(f"> {len(not_found)} IDs not found in TransportDataGouv")

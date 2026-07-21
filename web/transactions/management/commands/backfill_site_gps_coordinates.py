import time

from django.core.management.base import BaseCommand
from django.db.models import Q

from entity.services.geolocation import build_site_address, resolve_gps_coordinates
from transactions.models.site import Site

CHUNK_SIZE = 1000


class Command(BaseCommand):
    help = "Backfill GPS coordinates for sites missing them, with API rate limiting."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            choices=["true", "false"],
            default="true",
            help="Simulate updates without saving to database",
        )
        parser.add_argument(
            "--rate-limit",
            type=float,
            default=30.0,
            help="Maximum API requests per second (default: 30)",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Maximum number of sites to process",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"] == "true"
        rate_limit = options["rate_limit"]
        limit = options["limit"]

        if rate_limit <= 0:
            self.stderr.write(self.style.ERROR("--rate-limit must be greater than 0"))
            return

        min_interval = 1.0 / rate_limit
        last_request_at = None

        queryset = Site.objects.filter(Q(gps_coordinates__isnull=True) | Q(gps_coordinates="")).select_related("country")
        if limit:
            queryset = queryset[:limit]

        stats = {
            "processed": 0,
            "skipped_no_address": 0,
            "lookups": 0,
            "updated": 0,
            "not_found": 0,
        }

        for site in queryset.iterator(chunk_size=CHUNK_SIZE):
            stats["processed"] += 1
            address = build_site_address(site)
            if not address:
                stats["skipped_no_address"] += 1
                self.stdout.write(self.style.WARNING(f"Skipping site #{site.id}: no usable address"))
                continue

            self.stdout.write(f"Processing site #{site.id}: {address}")
            if last_request_at is not None:
                elapsed = time.monotonic() - last_request_at
                if elapsed < min_interval:
                    time.sleep(min_interval - elapsed)

            coords = resolve_gps_coordinates(address)
            last_request_at = time.monotonic()
            stats["lookups"] += 1

            if not coords:
                stats["not_found"] += 1
                self.stdout.write(self.style.WARNING(f"Processed site #{site.id}: coordinates not found"))
                continue

            site.gps_coordinates = coords
            if not dry_run:
                site.save(update_fields=["gps_coordinates"])
            stats["updated"] += 1
            self.stdout.write(self.style.SUCCESS(f"Processed site #{site.id}: {site.gps_coordinates}"))

        self.stdout.write("")
        self.stdout.write("=" * 50)
        self.stdout.write(self.style.SUCCESS(f"Processed: {stats['processed']} sites"))
        self.stdout.write(self.style.WARNING(f"Skipped (no address): {stats['skipped_no_address']} sites"))
        self.stdout.write(self.style.SUCCESS(f"Lookups performed: {stats['lookups']}"))
        self.stdout.write(self.style.SUCCESS(f"Updated: {stats['updated']} sites"))
        self.stdout.write(self.style.WARNING(f"Not found: {stats['not_found']} sites"))
        if dry_run:
            self.stdout.write(self.style.NOTICE("DRY RUN - No changes saved to database"))

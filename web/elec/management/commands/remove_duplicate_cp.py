# Importer les modules
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db.models import Count, Max, OuterRef, Subquery

from elec.models import ElecChargePoint, ElecMeterReading


class Command(BaseCommand):
    help = "Delete duplicate charge points"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            choices=["true", "false"],
            help="Dry run mode by default, no pdc deleted.",
            default="true",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"] == "true"

        if dry_run:
            self.stdout.write(" -- Running in dry run mode. No charge points deleted.")
        else:
            self.stdout.write(" -- Executing deletion of duplicate charge points.")

        # Subquery to get charge points with at least 2 occurrences
        duplicate_charge_points = (
            ElecChargePoint.objects.values("charge_point_id")
            .annotate(count=Count("charge_point_id"))
            .filter(count__gt=1)
            .values("charge_point_id")
        )
        # Get charge points objects
        charge_points = ElecChargePoint.objects.filter(charge_point_id__in=Subquery(duplicate_charge_points))

        self.stdout.write(f"Nombre de doublons : {charge_points.count()}")
        self.stdout.write(f"Nombre de pdc à conserver : {len(duplicate_charge_points)}")

        # Subquery to get the most recent reading date for each charge point
        latest_readings = (
            ElecMeterReading.objects.filter(meter__charge_point_id=OuterRef("charge_point_id"))
            .values("meter__charge_point_id")
            .annotate(latest_reading_date=Max("reading_date"))
            .values("latest_reading_date")
        )

        # Annotate the main query with the latest reading date
        queryset = (
            charge_points.annotate(latest_reading_date=Subquery(latest_readings.values("reading_date")[:1]))
            .values("id", "charge_point_id", "latest_reading_date")
            .order_by("charge_point_id")
        )

        # Group charge points by charge point ID
        grouped_charge_points = defaultdict(list)
        for item in queryset:
            grouped_charge_points[item["charge_point_id"]].append(item)

        ids_to_keep = []

        # For each group of charge points, apply rules to select the one to keep
        for _, items in grouped_charge_points.items():
            # Keep charge points wiht reading
            with_reading = [item for item in items if item["latest_reading_date"] is not None]

            if with_reading:
                # If there are, we keep the one with the more recent reading
                selected_point = max(with_reading, key=lambda x: x["latest_reading_date"])
            else:
                # Else we keep the one with the lowest ID (first created)
                selected_point = min(items, key=lambda x: x["id"])

            # Add charge point ID to the list of IDs to keep
            ids_to_keep.append(selected_point["id"])

        # Delete all charge points that are not in the list of IDs to keep
        charge_points_to_delete = charge_points.exclude(id__in=ids_to_keep)
        self.stdout.write(f"Points de charge à supprimer : {charge_points_to_delete.count()}")

        if not dry_run:
            charge_points_to_delete.delete()
            self.stdout.write("Points de charge supprimés !")

        self.stdout.write(f"Points de charge conservés : {len(ids_to_keep)}")

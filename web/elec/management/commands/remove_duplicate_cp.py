# Importer les modules
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db.models import Count, F, Subquery

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

        # Subquery to get not deleted charge points with at least 2 occurrences
        duplicate_charge_points = (
            ElecChargePoint.objects.values("charge_point_id")
            .annotate(count=Count("charge_point_id"))
            .filter(count__gt=1, is_deleted=False)
            .values("charge_point_id")
        )
        # Get charge points objects
        charge_points = ElecChargePoint.objects.filter(charge_point_id__in=Subquery(duplicate_charge_points))

        self.stdout.write(f"Nombre de doublons : {charge_points.count()}")
        self.stdout.write(f"Nombre de pdc à conserver : {len(duplicate_charge_points)}")

        # Get all charge points with their meter readings if they have any, otherwise None
        queryset = (
            ElecChargePoint.objects.filter(charge_point_id__in=charge_points.values("charge_point_id"))
            .prefetch_related("elecmeter_set__elecmeterreading_set")
            .annotate(
                meter_id=F("elec_meters__id"),
                reading_date=F("elec_meters__elec_meter_readings__reading_date"),
                reading_id=F("elec_meters__elec_meter_readings__id"),
            )
            .values("id", "charge_point_id", "meter_id", "reading_date", "reading_id")
        )

        # Group charge points by charge point ID
        grouped_charge_points = defaultdict(list)
        for item in queryset:
            grouped_charge_points[item["charge_point_id"]].append(item)

        ids_to_keep = []

        # For each group of charge points, apply rules to select the one to keep
        for _, items in grouped_charge_points.items():
            # Keep charge points wiht reading
            with_reading = [item for item in items if item["reading_date"] is not None]

            if with_reading:
                # If there are, we keep the one with the more recent reading
                # And we associate meter readings to the selected charge point
                selected_point = max(with_reading, key=lambda x: x["reading_date"])
                non_selected_points = [item for item in with_reading if item["id"] != selected_point["id"]]
                for old_charge_point in non_selected_points:
                    if not dry_run:
                        ElecMeterReading.objects.filter(id=old_charge_point["reading_id"]).update(
                            meter=selected_point["meter_id"]
                        )
                    self.stdout.write(
                        f"['meter_reading_id':{old_charge_point["reading_id"]}, 'from meter_id':{old_charge_point['meter_id']}, 'to meter_id':{selected_point['meter_id']}]"  # noqa: E501
                    )
            else:
                # Else we keep the one with the lowest ID (first created)
                selected_point = min(items, key=lambda x: x["id"])

            # Add charge point ID to the list of IDs to keep
            ids_to_keep.append(selected_point["id"])

        # Delete all charge points that are not in the list of IDs to keep
        charge_points_to_delete = charge_points.exclude(id__in=ids_to_keep)
        self.stdout.write(f"Points de charge à supprimer : {charge_points_to_delete.count()}")
        self.stdout.write(f"Points de charge à supprimer : {list(charge_points_to_delete.values_list('id', flat=True))}")

        if not dry_run:
            charge_points_to_delete.delete()
            self.stdout.write("Points de charge supprimés !")

        self.stdout.write(f"Points de charge conservés : {len(ids_to_keep)}")

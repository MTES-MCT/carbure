import logging

import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from simple_history.utils import bulk_update_with_history

from elec.models.elec_charge_point import ElecChargePoint
from elec.services.transport_data_gouv import TransportDataGouv

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

        try:
            df_map = pd.read_excel(file)
        except Exception as e:
            raise CommandError(f"Failed to read Excel file: {e}")

        # Rename only the first three columns
        cols = list(df_map.columns)
        if len(cols) < 2:
            raise CommandError("Excel file must contain at least two columns.")
        df_map.rename(columns={cols[0]: "old_id", cols[1]: "new_id"}, inplace=True)

        df_map = df_map[["old_id", "new_id"]].dropna(how="all")
        mapping_id = df_map.set_index("old_id")["new_id"].to_dict()
        self.stdout.write(self.style.SUCCESS(f"> Loaded {len(mapping_id)} mappings from {file}"))

        pdcs = ElecChargePoint.objects.filter(cpo__name__icontains=cpo, charge_point_id__in=mapping_id.keys())
        total = pdcs.count()
        self.stdout.write(self.style.SUCCESS(f"> Found {total} PDCs to update."))

        df_new = pd.DataFrame({"charge_point_id": list(mapping_id.values())})
        df_tdg: pd.DataFrame = TransportDataGouv.get_transport_data(df_new)
        df_tdg = df_tdg.set_index("charge_point_id")

        updated = []
        deleted = []
        not_found = []

        # Use transaction per batch
        for pdc in pdcs.iterator():
            old_id = pdc.charge_point_id
            new_id = mapping_id.get(old_id)

            # PDCs without a new ID will be marked as deleted
            if pd.isna(new_id):
                pdc.is_deleted = True
                deleted.append(pdc)
                continue

            # check that the new id exists on TDG
            try:
                record = df_tdg.loc[new_id]
            except Exception:
                not_found.append(old_id)
                continue

            new_station = record["station_id"]
            if pdc.charge_point_id != new_id or pdc.station_id != new_station:
                pdc.charge_point_id = new_id
                pdc.station_id = new_station
                updated.append(pdc)

        if apply:
            bulk_update_with_history(updated, ElecChargePoint, ["charge_point_id", "station_id"], 1000)
            bulk_update_with_history(deleted, ElecChargePoint, ["is_deleted"], 1000)
            self.stdout.write(self.style.SUCCESS(f"> Successfully updated {total - len(not_found) - len(deleted)} PDCs"))

        if deleted:
            self.stdout.write(self.style.WARNING(f"> {len(deleted)} PDCs marked as deleted"))
        if not_found:
            self.stdout.write(self.style.WARNING(f"> {len(not_found)} IDs not found in TransportDataGouv"))

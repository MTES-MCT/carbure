import os

import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction

from transactions.models.site import Site


class Command(BaseCommand):
    help = "Normalize depot customs IDs from DGDDI Excel file"

    DGDDI_DEPOTS_FILENAME = "Recensement_des_entrepots_suspensifs_PE__METRO+DOM__v2.xlsx"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            choices=["true", "false"],
            default="true",
            help="Simulate changes without saving to database",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run") == "true"

        # Load DGDDI depots file
        carbure_home = os.environ.get("CARBURE_HOME")
        if not carbure_home:
            self.stderr.write(self.style.ERROR("CARBURE_HOME environment variable not set"))
            return

        dgddi_depots_filepath = os.path.join(carbure_home, "web", "transactions", "fixtures", self.DGDDI_DEPOTS_FILENAME)

        if not os.path.exists(dgddi_depots_filepath):
            self.stderr.write(self.style.ERROR(f"File not found: {dgddi_depots_filepath}"))
            return

        try:
            df_dgddi = pd.read_excel(dgddi_depots_filepath, sheet_name="Entrepôts suspensifs (METRO)")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to read Excel file: {e}"))
            return

        depots = Site.objects.filter(site_type__in=[Site.EFS, Site.EFPE, Site.EFCA])

        stats = {"processed": 0, "updated": 0, "skipped": 0}

        with transaction.atomic():
            for depot in depots:
                stats["processed"] += 1
                customs_id = depot.customs_id

                if not customs_id:
                    self.stdout.write(f"Depot ID {depot.id}: no customs_id, skipping")
                    stats["skipped"] += 1
                    continue

                self.stdout.write(f"Processing depot ID {depot.id} with customs ID '{customs_id}'")

                # Normalize customs_id
                original_customs_id = customs_id
                if not customs_id.startswith("FR"):
                    customs_id = "FR" + customs_id.zfill(11)
                elif not customs_id.startswith("FR0") and len(customs_id) != 13:
                    customs_id = "FR" + customs_id[2:].zfill(11)

                if len(customs_id) != 13:
                    self.stdout.write(
                        self.style.WARNING(f" - Invalid customs ID '{original_customs_id}' -> '{customs_id}', skipping")
                    )
                    stats["skipped"] += 1
                    continue

                self.stdout.write(f" - Normalized customs ID: '{customs_id}'")

                # Search for accise number
                accise = None
                found_depot = df_dgddi.loc[
                    df_dgddi["NUMERO DU DEPOT"] == customs_id,
                    ["NUMERO AGREMENT DU TITULAIRE DU DEPOT"],
                ].values

                if len(found_depot) > 0:
                    accise = found_depot[0][0]
                elif "W" in customs_id:
                    found_depot = df_dgddi.loc[
                        df_dgddi["NUMERO AGREMENT DU TITULAIRE DU DEPOT"] == customs_id,
                        ["NUMERO DU DEPOT"],
                    ].values

                    if len(found_depot) > 0:
                        accise = customs_id
                        customs_id = found_depot[0][0]
                    else:
                        self.stdout.write(
                            self.style.WARNING(f" - No matching depot found in DGDDI file for customs ID '{customs_id}'")
                        )
                else:
                    self.stdout.write(
                        self.style.WARNING(f" - No matching depot found in DGDDI file for customs ID '{customs_id}'")
                    )

                # Update depot
                changed = False
                if depot.customs_id != customs_id:
                    depot.customs_id = customs_id
                    changed = True
                    self.stdout.write(self.style.SUCCESS(f" - Updated (customs_id: {customs_id})"))

                if accise and depot.accise != accise:
                    depot.accise = accise
                    changed = True
                    self.stdout.write(self.style.SUCCESS(f" - Updated (accise: {accise or 'N/A'})"))

                if changed:
                    if not dry_run:
                        depot.save()
                    stats["updated"] += 1

        # Print summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS(f"Processed: {stats['processed']} depots"))
        self.stdout.write(self.style.SUCCESS(f"Updated: {stats['updated']} depots"))
        self.stdout.write(self.style.WARNING(f"Skipped: {stats['skipped']} depots"))
        if dry_run:
            self.stdout.write(self.style.NOTICE("DRY RUN - No changes saved to database"))

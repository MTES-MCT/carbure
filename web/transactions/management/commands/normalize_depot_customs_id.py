import os

import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Entity
from entity.models import EntityScope
from entity.views.depots.mixins.create import get_gps_coordinates
from transactions.models.depot import Depot
from transactions.models.site import Site


class Command(BaseCommand):
    """
    Management command to normalize depot customs IDs from DGDDI Excel file.

    python web/manage.py normalize_depot_customs_id --dry-run=true
    python web/manage.py normalize_depot_customs_id --dry-run=false

    """

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

        stats = {"processed": 0, "updated": 0, "skipped": 0, "bureau_not_found": 0}

        with transaction.atomic():
            for depot in depots:
                stats["processed"] += 1
                customs_id = depot.customs_id

                # Very specific case
                if customs_id == "FR000000521":
                    customs_id = "FR00000000521"

                # Other very specific case
                WRONG_CUSTOMS_ID = {
                    "FR001265W2102": "FR00000001265",
                    "FR001229W2102": "FR00000001229",
                    "FR001346W2102": "FR00000001346",
                }

                if not customs_id:
                    self.stdout.write(f"Depot ID {depot.id}: no customs_id, skipping")
                    stats["skipped"] += 1
                    continue

                self.stdout.write(f"Processing depot ID {depot.id} with customs ID '{customs_id}'")

                # Normalize customs_id
                original_customs_id = customs_id

                if customs_id in WRONG_CUSTOMS_ID:
                    customs_id = WRONG_CUSTOMS_ID[customs_id]

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

                    if original_customs_id in WRONG_CUSTOMS_ID:
                        accise = original_customs_id

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

                # Update GPS coordinates if None
                if not depot.gps_coordinates:
                    gps_updated = self.update_gps_coordinates(depot)
                    if gps_updated:
                        changed = True

                # Search for "bureau de rattachement du dépot"
                found_office = df_dgddi.loc[
                    df_dgddi["NUMERO DU DEPOT"] == customs_id,
                    ["BUREAU DE RATTACHEMENT DU DEPOT"],
                ].values

                if len(found_office) > 0:
                    office_name = found_office[0][0]
                    self.stdout.write(self.style.SUCCESS(f" - Found (bureau de rattachement: {office_name})"))
                else:
                    office_name = None
                    self.stdout.write(
                        self.style.WARNING(
                            f" - No matching 'bureau de rattachement du dépot' found in DGDDI file "
                            f"for customs ID '{customs_id}'"
                        )
                    )
                    stats["bureau_not_found"] += 1

                if changed:
                    if not dry_run:
                        depot.save()
                    stats["updated"] += 1

                # Link depot to DGGDI entity (external admin) using EntityScope
                if office_name:
                    if not dry_run:
                        self.link_depot_to_dgddi_entity(depot, office_name)
                    self.stdout.write(self.style.SUCCESS(f" - Linked to DGDDI entity {self.rename_entity(office_name)}"))

        # Print summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS(f"Processed: {stats['processed']} depots"))
        self.stdout.write(self.style.SUCCESS(f"Updated: {stats['updated']} depots"))
        self.stdout.write(self.style.WARNING(f"Skipped: {stats['skipped']} depots"))
        self.stdout.write(self.style.WARNING(f"Bureau not found: {stats['bureau_not_found']} depots"))
        if dry_run:
            self.stdout.write(self.style.NOTICE("DRY RUN - No changes saved to database"))

    def rename_entity(self, name):
        if "bureau" in name.strip():
            name = name.replace("bureau", "").strip()
        return f"Bureau DGDDI - {name}"

    def link_depot_to_dgddi_entity(self, depot, office_name):
        from django.contrib.contenttypes.models import ContentType

        depot_ct = ContentType.objects.get_for_model(Depot)
        bureau_dgddi_name = self.rename_entity(office_name)
        dgddi_entity = Entity.objects.filter(name=bureau_dgddi_name, entity_type=Entity.EXTERNAL_ADMIN).first()

        scope, created = EntityScope.objects.get_or_create(
            entity=dgddi_entity,
            content_type=depot_ct,
            object_id=depot.id,
        )

    def update_gps_coordinates(self, depot):
        depot.gps_coordinates = get_gps_coordinates(depot)
        if depot.gps_coordinates:
            self.stdout.write(self.style.SUCCESS(f" - Updated (gps_coordinates: {depot.gps_coordinates})"))
            return True
        return False

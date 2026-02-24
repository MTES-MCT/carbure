import os

import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from biomethane.models.biomethane_production_unit import BiomethaneProductionUnit
from core.models import Department, Entity


class Command(BaseCommand):
    """
    Management command to import biomethane producers from Excel file.

    python web/manage.py import_biomethane_producers --dry-run=true
    python web/manage.py import_biomethane_producers --dry-run=false

    """

    help = "Import biomethane producers from Excel file"

    FILENAME = "biomethane_producers.xlsx"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            choices=["true", "false"],
            default="true",
            help="Simulate changes without saving to database",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run") == "true"

        filepath = self.get_xlsx_file_path()
        if not filepath:
            return

        self.import_producers(filepath, dry_run)

    def get_xlsx_file_path(self):
        """Return the path to the XLSX file to import."""
        carbure_home = os.environ.get("CARBURE_HOME")
        if not carbure_home:
            self.stderr.write(self.style.ERROR("CARBURE_HOME environment variable not set"))
            return

        filepath = os.path.join(carbure_home, "web", "biomethane", "fixtures", self.FILENAME)

        if not os.path.exists(filepath):
            self.stderr.write(self.style.ERROR(f"File not found: {filepath}"))
            return

        return filepath

    def import_producers(self, filepath, dry_run):
        try:
            df = pd.read_excel(filepath)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to read Excel file: {e}"))
            return

        # Check required columns
        required_columns = ["Installation de production", "Département", "SIRET"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            self.stderr.write(self.style.ERROR(f"Missing required columns: {', '.join(missing_columns)}"))
            return

        stats = {"processed": 0, "created": 0, "skipped": 0}

        producers_to_create = []
        production_unit_data = []

        departments = {d.code_dept: d for d in Department.objects.all()}

        with transaction.atomic():
            for _, row in df.iterrows():
                stats["processed"] += 1

                name = row["Installation de production"]
                siret = str(row["SIRET"]) if pd.notna(row["SIRET"]) else None
                department_code = str(row["Département"]).zfill(2) if pd.notna(row["Département"]) else None

                if not siret or len(siret) != 14:
                    stats["skipped"] += 1
                    self.stdout.write(
                        self.style.WARNING(f"Row {stats['processed']}: Invalid or missing SIRET '{siret}', skipping")
                    )
                    continue

                if Entity.all_objects.filter(entity_type=Entity.BIOMETHANE_PRODUCER, name=name).exists():
                    stats["skipped"] += 1
                    self.stdout.write(
                        self.style.WARNING(f"Row {stats['processed']}: Producer with name '{name}' already exists, skipping")
                    )
                    continue

                if BiomethaneProductionUnit.objects.filter(Q(site_siret=siret) | Q(name=name)).exists():
                    stats["skipped"] += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"Row {stats['processed']}: Production unit with SIRET '{siret}' or name '{name}' already exists"
                            ", skipping"
                        )
                    )
                    continue

                producers_to_create.append(
                    Entity(
                        name=name,
                        entity_type=Entity.BIOMETHANE_PRODUCER,
                    )
                )

                production_unit_data.append(
                    {
                        "name": name,
                        # "site_siret": siret, # not wanted anymore
                        "department": departments.get(department_code),
                    }
                )

                stats["created"] += 1

            if not dry_run:
                names_to_create = [e.name for e in producers_to_create]
                Entity.objects.bulk_create(producers_to_create)
                # Re-fetch from DB because MySQL bulk_create doesn't return PKs
                entity_by_name = {e.name: e for e in Entity.objects.filter(name__in=names_to_create)}

                for data in production_unit_data:
                    # Can't bulk_create because BiomethaneProductionUnit is an inherited model
                    BiomethaneProductionUnit.objects.create(
                        name=data["name"],
                        # site_siret=data["site_siret"],
                        department=data["department"],
                        producer=entity_by_name[data["name"]],
                    )

        # Print summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS(f"Processed: {stats['processed']} rows"))
        self.stdout.write(self.style.SUCCESS(f"Created: {stats['created']} producers"))
        self.stdout.write(self.style.WARNING(f"Skipped: {stats['skipped']} rows"))
        if dry_run:
            self.stdout.write(self.style.NOTICE("DRY RUN - No changes saved to database"))

import logging
import os

import pandas as pd
from django.core.management.base import BaseCommand, CommandError

from core import private_storage
from core.models import Entity
from tiruert.models import FossilFuel, MacFossilFuel

S3_FOLDER = "mac/"
BACKUP_S3_FOLDER = "mac/backups/"
TMP_FOLDER = "/tmp/mac/"

SHEET_NAMES = [
    "Gazole",
    "Essence",
    "Carburéacteur",
]

logger = logging.getLogger("mac_import")


class Command(BaseCommand):
    help = "Import 'mises à consommation' of fossil fuels from an excel file"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        logger.info("--- Starting MAC import ---")
        filename = self.get_file_to_import()
        # filename = "mac.xlsx"

        mac_rows = self.parse_mac_excel(f"{TMP_FOLDER}{filename}")
        logger.info(f"Found {len(mac_rows)} aggregated MACs in the file")

        mac_objects, entities = self.data_validation(mac_rows)
        logger.info(f"Validated {len(mac_objects)} MACs")

        self.update_entities(entities)
        logger.info(f"{len(entities)} entities updated")

        self.insert_mac_objects(mac_objects)
        logger.info("--- MAC import finished ---\n\n")

    def get_file_to_import(self, folder=S3_FOLDER):
        """
        Get the more recent file in the folder
        """
        files = private_storage.listdir(folder)[1]
        if not files:
            raise CommandError(f"No files found in {folder}")

        if len(files) == 1:
            latest_file = files[0]
        else:
            self.stdout.write("Multiple files found, getting the most recent one")
            files_with_mtime = [(file, private_storage.modified(os.path.join(folder, file))) for file in files]
            latest_file = max(files_with_mtime, key=lambda x: x[1])[0]

        self.download_file_from_S3(folder, latest_file)
        self.backup_file_after_dl(folder, latest_file)

        return latest_file

    def download_file_from_S3(self, folder, filename):
        """
        Download file from S3 to local tmp folder
        """

        def create_tmp_folder(folder):
            if not os.path.exists(folder):
                os.makedirs(folder)

        s3_path = f"{folder}{filename}"
        create_tmp_folder(TMP_FOLDER)

        with private_storage.open(f"{s3_path}", "rb") as f:
            tmp_path = f"{TMP_FOLDER}{filename}"
            with open(f"{tmp_path}", "wb") as f2:
                f2.write(f.read())

        logger.info(f"File downloaded successfully to {tmp_path}")

    def backup_file_after_dl(self, folder, filename, backup_folder=BACKUP_S3_FOLDER):
        """
        Move file to backup folder after download
        """
        s3_path = f"{folder}{filename}"
        backup_path = f"{backup_folder}{filename}"
        with private_storage.open(s3_path, "rb") as f:
            private_storage.save(backup_path, f)
        logger.info("File backed up successfully")

    def parse_mac_excel(self, filepath, sheet_names=SHEET_NAMES):
        """
        Parse the excel file and return a list of dictionaries
        """
        rows = [self._process_sheet(filepath, sheet_name) for sheet_name in sheet_names]
        list_rows = [row for sheet_rows in rows for row in sheet_rows]

        return list_rows

    def _process_sheet(self, filepath, sheet_name):
        df = pd.read_excel(filepath, sheet_name=sheet_name)
        mac_rows = []
        columns = df.columns[3:]
        columns = [col for col in columns if pd.notna(col)]
        if len(columns) == 0:
            raise CommandError(f"No valid columns found in sheet {sheet_name}")

        yellow_col_indices = list(range(3, 3 + len(columns)))

        for row in df.itertuples(index=False):
            siren_val = row[1]
            siren = str(int(siren_val)) if not pd.isna(siren_val) else ""
            for idx, col_idx in enumerate(yellow_col_indices):
                volume = row[col_idx]
                if pd.isna(volume) or volume == "":
                    continue
                fuel_nomenclature = columns[idx]
                mac_rows.append(
                    {
                        "siren": siren,
                        "fuel_nomenclature": fuel_nomenclature,
                        "period": 202501,
                        "volume": int(volume),
                        "start_date": "2025-01-01",
                        "end_date": "2025-12-31",
                        "year": 2025,
                    }
                )
        return mac_rows

    def data_validation(self, mac_rows):
        """
        Consolidate the data and check for errors
        """
        not_found_sirens = set()
        not_found_fuels = set()
        entity_cache = {}
        fuel_cache = {}
        errors = set()
        validate_macs = []

        for row in mac_rows:
            if row["siren"] in not_found_sirens:
                # errors.add(f"Entity with SIREN {row['siren']} not found")
                continue

            # Consolidate siren
            if row["siren"] in entity_cache:
                entity = entity_cache[row["siren"]]
            else:
                try:
                    entity = Entity.objects.get(registration_id=row["siren"], entity_type=Entity.OPERATOR)
                    entity_cache[row["siren"]] = entity
                    logger.info(f"Entity found: {entity}")
                except Entity.DoesNotExist:
                    logger.error(f"Entity with SIREN {row['siren']} not found")
                    not_found_sirens.add(row["siren"])
                    continue
                except Entity.MultipleObjectsReturned:
                    errors.add(f"Multiple entities with SIREN {row['siren']} found")
                    continue

            # Consolidate fuel
            if row["fuel_nomenclature"] in not_found_fuels:
                errors.add(f"{row["siren"]} - Fuel with nomenclature {row['fuel_nomenclature']} doesn't exist")
                continue
            elif row["fuel_nomenclature"] in fuel_cache:
                fuel = fuel_cache[row["fuel_nomenclature"]]
            else:
                try:
                    fuel = FossilFuel.objects.get(nomenclature=row["fuel_nomenclature"])
                    fuel_cache[row["fuel_nomenclature"]] = fuel
                except FossilFuel.DoesNotExist:
                    errors.add(f"{row["siren"]} - Fuel with nomenclature {row['fuel_nomenclature']} doesn't exist")
                    not_found_fuels.add(row["fuel_nomenclature"])
                    continue

            validate_macs.append(
                MacFossilFuel(
                    operator=entity,
                    fuel=fuel,
                    period=row["period"],
                    volume=row["volume"],
                    start_date=row["start_date"],
                    end_date=row["end_date"],
                    year=row["year"],
                )
            )

        if len(errors) > 0:
            logger.error(f"{len(errors)} error(s) found during data validation:")
            for error in errors:
                logger.error(error)

        return validate_macs, entity_cache

    def insert_mac_objects(self, mac_objects):
        """
        Insert the validated MACs in bulk into the database
        TODO: How to handle udpates?
        """
        batch_size = 100
        for i in range(0, len(mac_objects), batch_size):
            MacFossilFuel.objects.bulk_create(
                mac_objects[i : i + 100],
                # update_conflicts=True,
                # update_fields=["volume"],
            )

        logger.info(f"{len(mac_objects)} MACs inserted successfully")

    def update_entities(self, entities):
        """
        Update 'is_tiruert_liable' to True for all entities in the list
        """
        Entity.objects.filter(id__in=[entity.id for entity in entities.values()]).update(is_tiruert_liable=True)

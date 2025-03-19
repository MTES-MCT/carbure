import logging
import os

import pandas as pd
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError

from core.models import Entity
from tiruert.models import FossilFuel, MacFossilFuel
from transactions.models import Depot

S3_FOLDER = "mac/"
BACKUP_S3_FOLDER = "mac/backups/"
TMP_FOLDER = "/tmp/mac/"

logger = logging.getLogger("mac_import")


class Command(BaseCommand):
    help = "Import 'mises à consommation' of fossil fuels from an excel file"

    def add_arguments(self, parser):
        pass
        # parser.add_argument("--ids", type=str, help="Download specific certificates")
        # parser.add_argument("--no-pdf", action="store_true", help="Download certificates without pdf")

    def handle(self, *args, **options):
        logger.info("--- Starting MAC import ---")
        # filename = self.get_file_to_import()
        filename = "mac.xlsx"

        mac_rows = self.parse_mac_excel(f"{TMP_FOLDER}{filename}")
        logger.info(f"Found {len(mac_rows)} aggregated MACs in the file")

        mac_objects = self.data_validation(mac_rows)
        logger.info(f"Validated {len(mac_objects)} MACs")

        self.insert_mac_objects(mac_objects)
        logger.info("--- MAC import finished ---\n\n")

    def get_file_to_import(self, folder=S3_FOLDER):
        """
        Get the more recent file in the folder
        """
        files = default_storage.listdir(folder)[1]
        if not files:
            raise CommandError(f"No files found in {folder}")

        if len(files) == 1:
            latest_file = files[0]
        else:
            self.stdout.write("Multiple files found, getting the most recent one")
            files_with_mtime = [(file, default_storage.modified(os.path.join(folder, file))) for file in files]
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

        with default_storage.open(f"{s3_path}", "rb") as f:
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
        with default_storage.open(s3_path, "rb") as f:
            default_storage.save(backup_path, f)
        logger.info("File backed up successfully")

    def parse_mac_excel(self, filepath):
        """
        Parse the excel file and return a list of dictionaries
        """
        df = pd.read_excel(filepath, sheet_name="Données brutes MAC")

        grouped_df = (
            df.groupby(
                [
                    "SIREN Redevable",
                    "N Accise Redevable",
                    "Nomenclature combinee",
                    "Année de MAC",
                    "Mois de MAC",
                    "Date de debut de periode",
                    "Fin de periode",
                ]
            )["Nombre d'unite"]
            .sum()
            .reset_index()
        )

        mac_rows = []

        for _, row in grouped_df.iterrows():
            siren = row["SIREN Redevable"]
            depot_customs_id = str(row["N Accise Redevable"])[5:8]  # keep only 3 characters
            fuel_nomenclature = row["Nomenclature combinee"]
            period = f"{row['Année de MAC']}{int(row['Mois de MAC']):02d}"  # YYYYMM
            volume = row["Nombre d'unite"] * 100  # convert hL to L
            start_date = row["Date de debut de periode"]
            end_date = row["Fin de periode"]
            year = row["Année de MAC"]

            mac_rows.append(
                {
                    "siren": str(siren),
                    "depot_customs_id": str(depot_customs_id),
                    "fuel_nomenclature": int(fuel_nomenclature),
                    "period": int(period),
                    "volume": int(volume),
                    "start_date": start_date,
                    "end_date": end_date,
                    "year": int(year),
                }
            )

        return mac_rows

    def data_validation(self, mac_rows):
        """
        Consolidate the data and check for errors
        """
        not_found_sirens = set()
        not_found_depots = set()
        not_found_fuels = set()
        entity_cache = {}
        depot_cache = {}
        fuel_cache = {}
        errors = set()
        validate_macs = []

        for row in mac_rows:
            if row["siren"] in not_found_sirens:
                errors.add(f"Entity with SIREN {row['siren']} not found")
                continue

            # Consolidate siren
            if row["siren"] in entity_cache:
                entity = entity_cache[row["siren"]]
            else:
                try:
                    entity = Entity.objects.get(registration_id=row["siren"], is_enabled=True, entity_type=Entity.OPERATOR)
                    entity_cache[row["siren"]] = entity
                    logger.info(f"Entity found: {entity}")
                except Entity.DoesNotExist:
                    errors.add(f"Entity with SIREN {row['siren']} not found")
                    not_found_sirens.add(row["siren"])
                    continue
                except Entity.MultipleObjectsReturned:
                    errors.add(f"Multiple entities with SIREN {row['siren']} found")

            # Consolidate depot
            if row["depot_customs_id"] in not_found_depots:
                depot = None
                errors.add(f"{row["siren"]} - Depot with accise number {row['depot_customs_id']} doesn't exist")
            elif row["depot_customs_id"] in depot_cache:
                depot = depot_cache[row["depot_customs_id"]]
            else:
                try:
                    depot = Depot.objects.get(customs_id=row["depot_customs_id"])
                    depot_cache[row["depot_customs_id"]] = depot
                except Depot.DoesNotExist:
                    errors.add(f"{row["siren"]} - Depot with accise number {row['depot_customs_id']} doesn't exist")
                    not_found_depots.add(row["depot_customs_id"])
                    depot = None

            # Consolidate fuel
            if row["fuel_nomenclature"] in not_found_fuels:
                fuel = None
                errors.add(f"{row["siren"]} - Fuel with nomenclature {row['fuel_nomenclature']} doesn't exist")
            elif row["fuel_nomenclature"] in fuel_cache:
                fuel = fuel_cache[row["fuel_nomenclature"]]
            else:
                try:
                    fuel = FossilFuel.objects.get(nomenclature__contains=row["fuel_nomenclature"])
                    fuel_cache[row["fuel_nomenclature"]] = fuel
                except FossilFuel.DoesNotExist:
                    errors.add(f"{row["siren"]} - Fuel with nomenclature {row['fuel_nomenclature']} doesn't exist")
                    continue

            validate_macs.append(
                MacFossilFuel(
                    operator=entity,
                    depot=depot,
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

        return validate_macs

    def insert_mac_objects(self, mac_objects):
        """
        Insert the validated MACs in bulk into the database
        If a MAC already exists (same operator, fuel, period), update the volume
        """
        batch_size = 100
        for i in range(0, len(mac_objects), batch_size):
            MacFossilFuel.objects.bulk_create(
                mac_objects[i : i + 100],
                # update_conflicts=True,
                # update_fields=["volume"],
            )

        logger.info(f"{len(mac_objects)} MACs inserted successfully")

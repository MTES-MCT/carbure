import logging
import os

import pandas as pd
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError

from core.models import Entity, Pays
from entity.views.registration.search_company import search_company_gouv_fr
from tiruert.models import FossilFuel, MacFossilFuel
from transactions.models import Depot

S3_FOLDER = "mac/"
BACKUP_S3_FOLDER = "mac/backups/"
TMP_FOLDER = "/tmp/mac/"

logger = logging.getLogger("mac_import")

authorized_sirens = [
    814959045,
    453346009,
    889082178,
    528448079,
    889212221,
    864500418,
    888185105,
    388955130,
    317007342,
    902013309,
    901972992,
    779075241,
    439730375,
    493479489,
    753251354,
    722000965,
    395003221,
    334690435,
    601251614,
    401818174,
    841236581,
    389934423,
    333306843,
    542034327,
    422510750,
    720801349,
    306094194,
    830375390,
    521502443,
    324790096,
    833442304,
    390982635,
    301862710,
    789034915,
    513024968,
    342466174,
    325366334,
    340722750,
    418245700,
    305800997,
    394579353,
    879113363,
    797280443,
    490924271,
    388301988,
    887634525,
    439793811,
    809164239,
    853498632,
    969502004,
    785950015,
    385267950,
    542010053,
    450036967,
    403427214,
    912510005,
    852602259,
    309024867,
    489638338,
    910701796,
    883330938,
    412186066,
    389838087,
    401004353,
    829708577,
    302700901,
    347873879,
    579500455,
    325079473,
    393536941,
    418541900,
    978042547,
    480050525,
    389220872,
    946050119,
    489173713,
    975420217,
    347389371,
    950722256,
    797476199,
    619802895,
    947351680,
    530054733,
    877779355,
    342706892,
    350041984,
    433533635,
    384316709,
    342925748,
    490348141,
    377850292,
    493415095,
    677280661,
    332855923,
    838911683,
    329382600,
    401517123,
    343134805,
    387924772,
    777347386,
    388678930,
    15550601,
    844763490,
    327788675,
    852506062,
    444845218,
    302180187,
    432827608,
    351766571,
    529916793,
    844395632,
    501525851,
    890849854,
    978036937,
    843715970,
    913493607,
    632820676,
    953594769,
    917974800,
    353663750,
    883750772,
    353908593,
    552048811,
    388021156,
    946851268,
    353597677,
    16250037,
    151000031,
    449398031,
    414225052,
    780130175,
    315281113,
    344059605,
    481361228,
    8820,
    353261555,
    912194354,
    533247979,
    352860639,
    491968947,
    956501100,
    531680445,
    303955876,
    448546028,
    562050401,
    404075731,
    337884559,
    437673239,
    383809605,
    492203815,
    492203215,
    509584009,
    979112018,
    304425291,
    586950313,
    780094983,
    819441411,
    807857818,
    702006297,
    393194824,
]


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
            depot_customs_id = str(row["N Accise Redevable"])[4:8]  # keep only 4 characters
            depot_customs_id = (
                int(depot_customs_id) if depot_customs_id.isdigit() else None
            )  # convert to int to remove leading 0
            fuel_nomenclature = row["Nomenclature combinee"]
            period = f"{row['Année de MAC']}{int(row['Mois de MAC']):02d}"  # YYYYMM
            volume = row["Nombre d'unite"] * 100  # convert hL to L
            start_date = row["Date de debut de periode"]
            end_date = row["Fin de periode"]
            year = row["Année de MAC"]

            if siren not in authorized_sirens:
                logger.error(f"Unauthorized SIREN {siren} found in the file")
                continue

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
                # errors.add(f"Entity with SIREN {row['siren']} not found")
                continue

            # Consolidate siren
            if row["siren"] in entity_cache:
                entity = entity_cache[row["siren"]]
            else:
                try:
                    entity = Entity.objects.get(registration_id=row["siren"])
                    entity_cache[row["siren"]] = entity
                    logger.info(f"Entity found: {entity}")
                except Entity.DoesNotExist:
                    # logger.info(f"Entity with SIREN {row['siren']} not found")
                    entity, error = self.search_company_gouv_fr(row["siren"])
                    if entity is None:
                        not_found_sirens.add(row["siren"])
                        errors.add(error)
                        continue
                    entity_cache[row["siren"]] = entity
                except Entity.MultipleObjectsReturned:
                    errors.add(f"Multiple entities with SIREN {row['siren']} found")
                    continue

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
                except Depot.MultipleObjectsReturned:
                    errors.add(f"{row["siren"]} - Multiple depots with accise number {row['depot_customs_id']} found")
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

    def search_company_gouv_fr(self, siren):
        try:
            logger.info(f"Searching company with SIREN {siren} via API")
            company_found = search_company_gouv_fr(siren)
        except Exception:
            error = f"Company with SIREN {siren} not found"
            return None, error

        logger.info(f"Company found: {company_found['nom_complet']}")

        company_siege = company_found["siege"]
        company_city = company_siege["libelle_commune"]
        company_zipcode = company_siege["code_postal"]
        company_address = company_siege["adresse"]
        string_to_remove = f"{company_zipcode} {company_city}"
        company_address = company_address.replace(string_to_remove, "")

        france = Pays.objects.get(code_pays="FR")

        try:
            entity = Entity.objects.create(
                name=company_found["nom_complet"],
                legal_name=company_found["nom_raison_sociale"],
                registration_id=company_found["siren"],
                registered_address=company_address,
                registered_city=company_siege["libelle_commune"],
                registered_zipcode=company_siege["code_postal"],
                registered_country=france,
                is_enabled=True,
                entity_type=Entity.OPERATOR,
                is_tiruert_liable=True,
            )
            logger.info(f"Entity with SIREN {siren} created successfully")
        except Exception as e:
            error = f"Error creating entity with SIREN {siren}, {e}"
            return None, error

        return entity, None

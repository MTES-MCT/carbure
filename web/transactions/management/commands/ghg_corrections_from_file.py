import os
from collections import defaultdict

import pandas as pd
import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import reverse

from core import private_storage
from core.models import CarbureLot

S3_FOLDER = "corrections/"
TMP_FOLDER = "/tmp/corrections/"

SHEET_NAMES = [
    "2024 New",
    "2025 New",
    # "test",
]

FIELDS_TO_UPDATE = [
    "eec",
    "el",
    "ep",
    "etd",
    "eu",
    "esca",
    "eccs",
    "eccr",
    "eee",
]

RECONCILIATION_KEY = "carbure_id"


class Command(BaseCommand):
    help = "Script to update wrong ghg data in the database from a file"

    def add_arguments(self, parser):
        parser.add_argument("--file", type=str, help="File to import", required=True)
        # sessionid : Used to authenticate the request and corresponding user email
        # will appear in history comments as "Modifié par"
        parser.add_argument("--sessionid", type=str, help="Authenticated user session", required=True)
        parser.add_argument("--csrftoken", type=str, help="CRSF token", required=True)

    def handle(self, *args, **options):
        self.stdout.write("--- Starting ghg correction script ---")

        file = self.download_file_from_S3(options["file"])

        correction_rows = self.parse_excel(f"{TMP_FOLDER}{file}")

        if len(correction_rows) > 0:
            valid_rows = self.data_validation(correction_rows)

        if len(valid_rows) > 0:
            self.update_lots(valid_rows, options["sessionid"], options["csrftoken"])

        self.stdout.write("--- Finished ghg correction script ---")

    def download_file_from_S3(self, filename, folder=S3_FOLDER):
        """
        Download file from S3 to local tmp folder
        """
        s3_path = f"{folder}{filename}"
        self._create_tmp_folder(TMP_FOLDER)

        with private_storage.open(f"{s3_path}", "rb") as f:
            tmp_path = f"{TMP_FOLDER}{filename}"
            with open(f"{tmp_path}", "wb") as f2:
                f2.write(f.read())

        self.stdout.write(f"File downloaded successfully to {tmp_path}", self.style.SUCCESS)
        return filename

    def _create_tmp_folder(self, folder):
        if not os.path.exists(folder):
            os.makedirs(folder)

    def parse_excel(self, filepath, sheet_names=SHEET_NAMES):
        """
        Parse the excel file and return a list of dictionaries
        """
        rows = [self._process_sheet(filepath, sheet_name) for sheet_name in sheet_names]
        list_rows = [row for sheet_rows in rows for row in sheet_rows]

        self.stdout.write(f"{len(list_rows)} lots have to be corrected")
        return list_rows

    def _process_sheet(self, filepath, sheet_name):
        """
        Process a single sheet and return its rows
        """
        try:
            df = pd.read_excel(filepath, sheet_name=sheet_name)
            rows = []
            for _, row in df.iterrows():
                row_data = {field: row[field] for field in FIELDS_TO_UPDATE + [RECONCILIATION_KEY]}
                rows.append(row_data)
            return rows
        except ValueError:
            self.stdout.write(f"Sheet {sheet_name} not found in the file", self.style.ERROR)
            return []

    def data_validation(self, rows):
        """
        Consolidate the data and check for errors
        """

        valid_rows = []

        existing_carbure_ids = set(CarbureLot.objects.values_list(RECONCILIATION_KEY, flat=True))

        for row in rows:
            if row[RECONCILIATION_KEY] not in existing_carbure_ids:
                self.stdout.write(f"Lot with carbure_id {row[RECONCILIATION_KEY]} not found", self.style.ERROR)
                continue
            if not all(field in row for field in FIELDS_TO_UPDATE):
                self.stdout.write(f"Missing fields in row: {row}", self.style.ERROR)
                continue
            if any(pd.isna(row[field]) for field in FIELDS_TO_UPDATE):
                self.stdout.write(f"Empty fields in row: {row}", self.style.ERROR)
                continue

            valid_rows.append(row)

        self.stdout.write(f"{len(valid_rows)} lots are found and will be updated", self.style.SUCCESS)
        return valid_rows

    def _analyze_changes(self, grouped_data):
        """
        Analyze changes and count the number of modifications for each field.
        """
        modification_counts = {field: 0 for field in FIELDS_TO_UPDATE}

        for update_key, group in grouped_data.items():
            carbure_ids = [row[RECONCILIATION_KEY] for row in group]
            existing_lots = CarbureLot.objects.filter(carbure_id__in=carbure_ids)

            for lot in existing_lots:
                for field in FIELDS_TO_UPDATE:
                    new_value = update_key[FIELDS_TO_UPDATE.index(field)]
                    current_value = getattr(lot, field, None)
                    if float(current_value) != float(new_value):
                        modification_counts[field] += 1

        # Display the analysis results
        self.stdout.write("=== Analysis of changes ===", self.style.SUCCESS)
        for field, count in modification_counts.items():
            self.stdout.write(f"{field}: {count} modifications")

    def update_lots(self, rows, sessionid, csrftoken):
        """
        Group lots by similar data, analyze changes, and call update_many() for each group.
        """
        # Group lots by similar data
        grouped_data = defaultdict(list)
        for row in rows:
            # Use a tuple of the values of the fields to update as the key
            update_key = tuple(row[field] for field in FIELDS_TO_UPDATE)
            grouped_data[update_key].append(row)

        # Call the analysis phase
        self._analyze_changes(grouped_data)

        # Call update_many() for each group
        self.stdout.write("=== Updating lots ===", self.style.SUCCESS)
        domain = settings.CSRF_TRUSTED_ORIGINS[0]
        url = reverse("transactions-admin-lots-update-many")
        endpoint_url = f"{domain}{url[1:]}"

        for update_key, group in grouped_data.items():
            carbure_ids = [row[RECONCILIATION_KEY] for row in group]
            existing_lots = CarbureLot.objects.filter(carbure_id__in=carbure_ids)

            # Prepare data for update_many
            lot_ids = [lot.id for lot in existing_lots]
            update_data = dict(zip(FIELDS_TO_UPDATE, update_key))

            # Configure the sessionid and crsftoken for authentication
            cookies = {
                "sessionid": sessionid,
                "csrftoken": csrftoken,
            }

            headers = {
                "X-CSRFToken": csrftoken,
                "Referer": endpoint_url,
            }

            # Convert the payload to form-data format
            payload = {
                "entity_id": 9,
                "lots_ids": lot_ids,
                "comment": "Modification erreur de calcul GES",
                "dry_run": "false",
            }
            payload.update({field: str(value) for field, value in update_data.items()})  # Add update fields

            # Call the endpoint to update the lots
            response = requests.post(endpoint_url, data=payload, cookies=cookies, headers=headers)

            # Handle the response
            if response.status_code != 200:
                self.stdout.write(f"Error while updating lots: {response.content}", self.style.ERROR)
            else:
                self.stdout.write(f"{len(lot_ids)} lots updated successfully")

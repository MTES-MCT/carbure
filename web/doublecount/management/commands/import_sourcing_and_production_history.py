import os
import time

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from doublecount.helpers import load_dc_production_history_data, load_dc_sourcing_history_data
from doublecount.models import DoubleCountingApplication
from doublecount.parser.dc_parser import parse_dc_excel

S3_FOLDER = "doublecounting/old/"
TMP_FOLDER = "/tmp/doublecounting/"


class Command(BaseCommand):
    help = "Download redcert certificates pdfs"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        start_time = time.time()

        self.download_files_from_S3(S3_FOLDER)
        self.process_xlsx_files(TMP_FOLDER)

        self.stdout.write(f"Time spent: {time.time() - start_time:.2f} seconds")
        self.stdout.write(self.style.SUCCESS("Script executed successfully"))

    def download_files_from_S3(self, folder):
        # Get all files in the folder and download them in TMP_FOLDER
        for file in default_storage.listdir(folder)[1]:
            s3_path = f"{folder}{file}"
            with default_storage.open(f"{s3_path}", "rb") as f:
                tmp_path = f"{TMP_FOLDER}{file}"
                with open(f"{tmp_path}", "wb") as f2:
                    f2.write(f.read())

    def process_xlsx_files(self, folder):
        # Process each xlsx file in the TMP_FOLDER
        for file_name in os.listdir(folder):
            if file_name.endswith(".xlsx"):
                file_path = os.path.join(folder, file_name)
                self.process_dc_application(file_path, file_name)

    def process_dc_application(self, file_path, filename):
        print(f"Processing file: {file_path}")

        dca = self.get_dca_from_filename(filename)

        if dca is None:
            return

        (
            info,
            sourcing_forecast_rows,
            production_max_rows,
            production_forecast_rows,
            requested_quota_rows,
            sourcing_history_rows,
            production_max_history_rows,
            production_effective_history_rows,
        ) = parse_dc_excel(file_path)

        production_history_data, production_history_errors = load_dc_production_history_data(
            dca, production_max_history_rows, production_effective_history_rows
        )

        sourcing_history_data, sourcing_history_errors = load_dc_sourcing_history_data(dca, sourcing_history_rows)

        if production_history_errors:
            self.stdout.write("production history errors", production_history_errors)
            return

        if sourcing_history_errors:
            self.stdout.write("sourcing history errors", sourcing_history_errors)
            return

        for sourcing_history in sourcing_history_data:
            sourcing_history.save()

        for production_history in production_history_data:
            production_history.save()

        self.stdout.write(self.style.SUCCESS(f"Processed DCA: {dca.certificate_id}"))

    def get_dca_from_filename(self, filename):
        # example filename: FR_089_2023.xlsx, keep only FR_089_2023
        dca_id = filename.split(".")[0]

        try:
            dca = DoubleCountingApplication.objects.filter(certificate_id=dca_id).first()
            self.stdout.write(f"DCA: {dca}")
        except DoubleCountingApplication.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"DCA not found for certificate_id: {dca_id}"))
            return None

        return dca

import os
import time
import traceback
import warnings

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from doublecount.helpers import load_dc_production_history_data, load_dc_sourcing_history_data
from doublecount.models import DoubleCountingApplication
from doublecount.parser.dc_parser import parse_dc_excel

S3_FOLDER = "doublecounting/old/"
TMP_FOLDER = "/tmp/doublecounting/"


class Command(BaseCommand):
    help = "Download redcert certificates pdfs"

    warnings.simplefilter("ignore", UserWarning)

    def add_arguments(self, parser):
        parser.add_argument("--id", type=str, help="DCA certificate_id")

    def handle(self, *args, **options):
        start_time = time.time()

        if options["id"]:
            self.process_dc_application(f"{TMP_FOLDER}{options["id"]}.xlsx", f"{options["id"]}.xlsx")
            return

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
                self.stdout.write("\n")
                self.process_dc_application(file_path, file_name)

    def process_dc_application(self, file_path, filename):
        self.stdout.write(f"Processing file: {file_path}")

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

        errors = False

        if production_history_errors:
            self.stdout.write(f"production history errors: {production_history_errors}")
            self.stdout.write(self.style.ERROR(f"Error processing DCA: {dca.certificate_id}"))
            errors = True

        if sourcing_history_errors:
            self.stdout.write(f"sourcing history errors: {sourcing_history_errors}")
            self.stdout.write(self.style.ERROR(f"Error processing DCA: {dca.certificate_id}"))
            errors = True

        if errors:
            return

        # Chek if sourcing history already exists for this dca
        if not dca.history_sourcing.exists():
            for sourcing_history in sourcing_history_data:
                sourcing_history.save()
                self.stdout.write("Sourcing history saved")
        else:
            self.stdout.write("Sourcing history already exists")

        # Chek if production history already exists for this dca
        if not dca.history_production.exists():
            for production_history in production_history_data:
                production_history.save()
                self.stdout.write("Production history saved")
        else:
            self.stdout.write("Production history already exists")

        s3_path = f"doublecounting/{dca.id}_application_{dca.certificate_id}.xlsx"

        self.update_dca_download_link(dca, s3_path)
        self.upload_dca_to_s3(s3_path, open(file_path, "rb"))

        self.stdout.write(self.style.SUCCESS(f"Processed DCA: {dca.certificate_id}"))

    def get_dca_from_filename(self, filename):
        # example filename: FR_089_2023.xlsx, keep only FR_089_2023
        dca_id = filename.split(".")[0]

        try:
            dca = DoubleCountingApplication.objects.get(certificate_id=dca_id)
            self.stdout.write(f"DCA: {dca}")
        except DoubleCountingApplication.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"DCA not found for certificate_id: {dca_id}"))
            return None
        except DoubleCountingApplication.MultipleObjectsReturned:
            self.stdout.write(self.style.ERROR(f"Multiple DCA found for certificate_id: {dca_id}"))
            return None

        return dca

    def update_dca_download_link(self, dca, s3_path):
        if dca.download_link:
            return

        dca.download_link = default_storage.url(s3_path)
        dca.save()

    def upload_dca_to_s3(self, s3_path, file):
        try:
            default_storage.save(s3_path, file)
        except Exception:
            traceback.print_exc()
            self.stdout.write(self.style.ERROR(f"Error uploading file to S3: {s3_path}"))

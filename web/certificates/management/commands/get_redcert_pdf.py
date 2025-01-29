import os
import shutil
import time

import undetected_chromedriver as uc
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from core.models import GenericCertificate

DOWNLOAD_DIR = "/tmp/certificates"
FINAL_DIR = "/tmp/certificates/final"
URL = "https://redcert.eu/ZertifikateDatenAnzeige.aspx"
S3_FOLDER = "certificates/"


class Command(BaseCommand):
    help = "Download redcert certificates pdfs"

    def add_arguments(self, parser):
        parser.add_argument("--ids", type=str, help="Download specific certificates")
        parser.add_argument("--no-pdf", action="store_true", help="Download certificates without pdf")

    def handle(self, *args, **options):
        start_time = time.time()
        self.create_directories()

        # Instanciate the chrome driver
        driver = self.create_driver()
        self.load_redcert_page(driver)

        certificates = None
        if options["ids"]:
            certificates = self.certificates_with_ids(options["ids"])
        elif options["no_pdf"]:
            certificates = self.certificates_without_pdf()

        if certificates:
            certificates_to_update = self.get_pdf_for_specific_certificates(driver, certificates)
        else:
            certificates_to_update = self.get_all_certificates(driver, start_time)

        driver.quit()

        self.update_certificates(certificates_to_update)
        self.upload_all_certs_to_S3(len(certificates_to_update))

        self.stdout.write(f"Time spent: {time.time() - start_time:.2f} seconds")
        self.stdout.write(self.style.SUCCESS("Script executed successfully"))

    def create_directories(self):
        # Create the download directories if they don't exist
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        os.makedirs(FINAL_DIR, exist_ok=True)

    def load_redcert_page(self, driver):
        # Add a timeout to prevent infinite loading
        timeout = 30
        driver.set_page_load_timeout(timeout)

        try:
            driver.get(URL)
        except TimeoutException:
            driver.quit()
            raise CommandError("Timeout : page not loaded in time")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//*[@id='ctl00_mainContentPlaceHolder_zertifikatIdentifikatorTextBox']",
                )
            )
        )

    def certificates_without_pdf(self):
        return GenericCertificate.objects.filter(
            certificate_type=GenericCertificate.REDCERT,
            download_link__isnull=True,
            valid_until__gte=time.strftime("%Y-%m-%d"),
        ).order_by("-valid_until")

    def certificates_with_ids(self, certificate_ids):
        return GenericCertificate.objects.filter(certificate_id__in=certificate_ids.split(","))

    def get_pdf_for_specific_certificates(self, driver, certificates):
        self.stdout.write("Searching for certificate with ids %s" % [c.certificate_id for c in certificates])

        certificates_to_update = []

        total = len(certificates)

        for i, certificate in enumerate(certificates):
            self.stdout.write(f"{i+1}/{total}: {certificate.certificate_id}")
            # Fill the form
            search_box = driver.find_element(
                By.XPATH, "//*[@id='ctl00_mainContentPlaceHolder_zertifikatIdentifikatorTextBox']"
            )
            search_box.clear()
            search_box.send_keys(certificate.certificate_id)

            # And submit
            search_box.send_keys(Keys.RETURN)

            # Wait until results are loaded
            time.sleep(5)

            rows = driver.find_elements(By.CSS_SELECTOR, "tr")
            rows = rows[1:]  # Remove the first row header

            if not rows:
                self.stdout.write("No results found for certificate %s" % certificate.certificate_id)
                continue

            try:
                self.download_certificate(
                    driver,
                    rows[0],
                    certificate,
                )
            except NoSuchElementException:
                self.stdout.write("No PDF found for certificate %s" % certificate.certificate_id)
            else:
                certificates_to_update.append(certificate)

        return certificates_to_update

    def get_all_certificates(self, driver, start_time):
        self.stdout.write("No id provided, downloading all certificates")

        select_element = driver.find_element(By.ID, "ctl00_mainContentPlaceHolder_searchStatusDELocalizedDropDownList")
        select = Select(select_element)

        # Select only valid certificates and submit form
        select.select_by_value("1")  # value="1"
        driver.find_element(By.XPATH, '//*[@id="ctl00_mainContentPlaceHolder_SearchButton"]').click()

        # Wait until results are loaded
        time.sleep(7)

        # Change the number of results per page to 100
        pagination_100 = driver.find_element(
            By.XPATH, '//*[@id="ctl00_mainContentPlaceHolder_PaginationControl_NumberOfPageResultsLarge"]'
        )
        pagination_100.click()

        # Wait until results are loaded, again...
        time.sleep(7)

        # Get all certificates with 'valid_until' date > today
        certificates = GenericCertificate.objects.filter(
            certificate_type=GenericCertificate.REDCERT,
            valid_until__gte=time.strftime("%Y-%m-%d"),
        )

        nb_pdf_downloaded = 0
        nb_skipped = 0
        nb_results = driver.find_element(By.ID, "ctl00_mainContentPlaceHolder_PaginationControl_TotalNumberOfResults").text
        nb_results = nb_results.split()[0]
        max_pages = int(nb_results) // 100 + 1
        certificates_to_update = []

        self.stdout.write(f"{max_pages} pages")

        for page_number in range(1, max_pages):
            if page_number > 1:
                self.go_to_next_page(driver, page_number)

            rows = driver.find_elements(By.CSS_SELECTOR, "tr")
            rows = rows[1:]  # Remove the first row header

            nb_pdf_downloaded, nb_skipped, certificates_to_udpate = self.download_certificates(
                driver,
                rows=rows,
                certificates=certificates,
                nb_pdf_downloaded=nb_pdf_downloaded,
                nb_skipped=nb_skipped,
            )

            certificates_to_update.extend(certificates_to_udpate)

            self.stdout.write(f"Time spent: {time.time() - start_time:.2f} seconds")
            self.stdout.write(f"Downloaded {nb_pdf_downloaded} pdfs")
            self.stdout.write(f"Skipped {nb_skipped} pdfs")

            if page_number % 10 == 0:
                self.go_to_next_10(driver)

        self.stdout.write(f"TOTAL Downloaded {nb_pdf_downloaded} pdfs")
        self.stdout.write(f"TOTAL Skipped {nb_skipped} pdfs")

        return certificates_to_update

    def download_certificates(self, driver, **kwargs):
        certificates = kwargs["certificates"]
        certificates_to_update = []

        for i, row in enumerate(kwargs["rows"]):
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 3:
                redcert_id = cells[2].text
                self.stdout.write(f"{i+1}/{len(kwargs["rows"])}: {redcert_id}")

                if redcert_id not in certificates.values_list("certificate_id", flat=True):
                    self.stdout.write("Skipping certificate %s" % redcert_id)
                    kwargs["nb_skipped"] += 1
                    continue

                try:
                    certificate = certificates.filter(certificate_id=redcert_id).first()

                    self.download_certificate(
                        driver,
                        row,
                        certificate,
                    )
                    kwargs["nb_pdf_downloaded"] += 1

                except NoSuchElementException:
                    self.stdout.write("No PDF found for certificate %s" % redcert_id)
                    kwargs["nb_skipped"] += 1

                else:
                    certificates_to_update.append(certificate)

        return kwargs["nb_pdf_downloaded"], kwargs["nb_skipped"], certificates_to_update

    def download_certificate(self, driver, row, certificate):
        try:
            dl_button = row.find_element(By.CLASS_NAME, "lastColumns").find_element(By.TAG_NAME, "input")
            actions = ActionChains(driver)
            actions.move_to_element(dl_button).click().perform()

            new_name = f"certificate_{certificate.certificate_id}.pdf"
            self.wait_for_download_and_move(new_name)
        except WebDriverException:
            raise NoSuchElementException

    def update_certificates(self, certificates_to_update):
        self.stdout.write("Updating certificates download links...")
        try:
            for certificate in certificates_to_update:
                s3_path = f"{S3_FOLDER}certificate_{certificate.certificate_id}.pdf"
                certificate.download_link = default_storage.url(s3_path)

            GenericCertificate.objects.bulk_update(certificates_to_update, ["download_link"])
        except Exception as e:
            raise CommandError(f"Error updating certificates: {e}")

    def go_to_next_10(self, driver):
        self.stdout.write("--> Going to next ten")
        try:
            next_page = driver.find_element(By.XPATH, "//input[@type='button' and @value='next-page']")
            actions = ActionChains(driver)
            actions.move_to_element(next_page).click().perform()

            time.sleep(6)

        except NoSuchElementException:
            self.stdout.write("No next ten")

        return

    def go_to_next_page(self, driver, page_number):
        self.stdout.write(f"--> Going to page {page_number}")
        try:
            next_page = driver.find_element(
                By.XPATH,
                f"//input[@type='button' and @value='{page_number}']",
            )
            actions = ActionChains(driver)
            actions.move_to_element(next_page).click().perform()

            time.sleep(6)

        except NoSuchElementException:
            self.stdout.write("No next page")

        return

    def create_driver(self):
        self.stdout.write("Creating new driver...")

        # Create ChromeOptions object
        options = uc.ChromeOptions()
        options.headless = True
        options.add_argument("--lang=en_US")
        options.add_experimental_option("prefs", {"intl.accept_languages": "en,en_US"})
        options.add_argument("--dns-prefetch-disable")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": DOWNLOAD_DIR,  # Définir le dossier de téléchargement
                "download.prompt_for_download": False,  # Désactiver les pop-ups de confirmation de téléchargement
                "download.directory_upgrade": True,  # Mettre à jour le dossier de téléchargement si nécessaire
                "plugins.always_open_pdf_externally": True,  # Ouvrir les fichiers PDF directement (ne pas les ouvrir dans Chrome) # noqa
            },
        )

        driver = uc.Chrome(options=options)
        self.stdout.write("Driver ready")
        return driver

    def wait_for_download_and_move(self, new_name):
        # Wait for completed download
        while True:
            crdownload_files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith(".crdownload")]
            pdf_files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith(".pdf") or f.endswith(".PDF")]

            # If there is a PDF file and no CRDOWNLOAD file, the download is finished
            if pdf_files and not crdownload_files:
                downloaded_file = os.path.join(DOWNLOAD_DIR, pdf_files[0])  # Take the first one
                final_path = os.path.join(FINAL_DIR, new_name)

                # Move and rename the file
                shutil.move(downloaded_file, final_path)
                break

            time.sleep(0.3)

    def upload_all_certs_to_S3(self, counter):
        self.stdout.write(f"Transferring {counter } files to S3...")

        for idx, file_name in enumerate(os.listdir(FINAL_DIR)):
            local_file_path = os.path.join(FINAL_DIR, file_name)

            if os.path.isfile(local_file_path):
                s3_path = f"{S3_FOLDER}{file_name}"

                with open(local_file_path, "rb") as f:
                    default_storage.save(s3_path, f)

                self.stdout.write(f"\r{idx + 1}/{counter}", ending="")

        # Delete folder
        shutil.rmtree(DOWNLOAD_DIR)

        self.stdout.write("\n")
        self.stdout.write("All files transferred to S3")

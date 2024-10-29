import time

import undetected_chromedriver as uc
from django.core.management.base import BaseCommand, CommandError
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from core.models import GenericCertificate


class Command(BaseCommand):
    help = "Download redcert certificates pdfs"

    def add_arguments(self, parser):
        parser.add_argument("--id", type=str, help="Download a specific certificate")

    def handle(self, *args, **options):
        url = "https://redcert.eu/ZertifikateDatenAnzeige.aspx"

        # Instanciate the chrome driver
        driver = self.create_driver()

        # Add a timeout to prevent infinite loading
        timeout = 30
        driver.set_page_load_timeout(timeout)

        try:
            driver.get(url)
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
        driver.save_screenshot("screenshot-form1.png")

        start_time = time.time()

        if options["id"]:
            self.stdout.write("Searching for certificate with id %s" % options["id"])
            # Fill the form
            search_box = driver.find_element(
                By.XPATH, "//*[@id='ctl00_mainContentPlaceHolder_zertifikatIdentifikatorTextBox']"
            )
            search_box.send_keys(options["id"])

            # And submit
            search_box.send_keys(Keys.RETURN)

            # Wait until results are loaded
            time.sleep(5)
            driver.save_screenshot("screenshot-form2.png")

            # Click on input element with src="Images/Apps/documentAcrobat.svg"
            dl_button = driver.find_element(
                By.XPATH,
                "//input[@type='image' and contains(@onclick, 'SelectedPDF$0')]",
            )

            dl_button.click()

            self.stdout.write("Click !")

            # Wait for the pdf to be downloaded
            time.sleep(3)
            self.stdout.write("pdf should be downloaded")

        else:
            self.stdout.write("No id provided, downloading all certificates")

            select_element = driver.find_element(By.ID, "ctl00_mainContentPlaceHolder_searchStatusDELocalizedDropDownList")
            select = Select(select_element)

            # Select only valid certificates
            select.select_by_value("1")  # value="1"

            # And submit form
            driver.find_element(By.XPATH, '//*[@id="ctl00_mainContentPlaceHolder_SearchButton"]').click()

            # Wait until results are loaded
            time.sleep(18)
            driver.save_screenshot("screenshot-form3.png")

            # Get all certificates with 'valid_until' date > today
            certificates = GenericCertificate.objects.filter(
                certificate_type=GenericCertificate.REDCERT, valid_until__gte=time.strftime("%Y-%m-%d")
            )

            certificate_ids = [c.certificate_id for c in certificates]

            pagination_100 = driver.find_element(
                By.XPATH, '//*[@id="ctl00_mainContentPlaceHolder_PaginationControl_NumberOfPageResultsLarge"]'
            )

            pagination_100.click()

            # Wait until results are loaded
            time.sleep(18)
            driver.save_screenshot("screenshot-form3.png")

            nb_pdf_downloaded = 0
            nb_skipped = 0
            nb_results = driver.find_element(
                By.ID, "ctl00_mainContentPlaceHolder_PaginationControl_TotalNumberOfResults"
            ).text
            nb_results = nb_results.split()[0]
            max_pages = int(nb_results) // 100 + 1
            self.stdout.write(f"{max_pages} pages")

            for page_number in range(1, max_pages):
                if page_number > 1:
                    self.go_to_next_page(driver, page_number)

                rows = driver.find_elements(By.CSS_SELECTOR, "tr")
                # Remove the first row header
                rows = rows[1:]

                nb_pdf_downloaded, nb_skipped = self.download_certificates(
                    driver,
                    rows=rows,
                    certificate_ids=certificate_ids,
                    nb_pdf_downloaded=nb_pdf_downloaded,
                    nb_skipped=nb_skipped,
                )

                self.stdout.write(f"Time spent: {time.time() - start_time:.2f} seconds")
                self.stdout.write(f"Downloaded {nb_pdf_downloaded} pdfs")
                self.stdout.write(f"Skipped {nb_skipped} pdfs")

                if page_number % 10 == 0:
                    self.go_to_next_10(driver)

        self.stdout.write(f"Time spent: {time.time() - start_time:.2f} seconds")
        self.stdout.write(f"Downloaded {nb_pdf_downloaded} pdfs")
        self.stdout.write(f"Skipped {nb_skipped} pdfs")
        driver.quit()

    def download_certificates(self, driver, **kwargs):
        for i, row in enumerate(kwargs["rows"]):
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 3:
                redcert_id = cells[2].text
                self.stdout.write(f"{i+1}/{len(kwargs["rows"])}: {redcert_id}")

                if redcert_id not in kwargs["certificate_ids"]:
                    self.stdout.write("Skipping certificate %s" % redcert_id)
                    kwargs["nb_skipped"] += 1
                    continue

                try:
                    dl_button = driver.find_element(
                        By.XPATH,
                        f"//input[@type='image' and contains(@onclick, 'SelectedPDF${i}')]",
                    )
                    actions = ActionChains(driver)
                    actions.move_to_element(dl_button).click().perform()

                    # Wait for the pdf to be downloaded
                    time.sleep(2)
                    kwargs["nb_pdf_downloaded"] += 1

                except NoSuchElementException:
                    self.stdout.write("No PDF found for certificate %s" % redcert_id)
                    kwargs["nb_skipped"] += 1

        return kwargs["nb_pdf_downloaded"], kwargs["nb_skipped"]

    def go_to_next_10(self, driver):
        self.stdout.write("--> Going to next ten")
        try:
            next_page = driver.find_element(By.XPATH, "//input[@type='button' and @value='next-page']")
            next_page.click()

            time.sleep(18)

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
            next_page.click()

            time.sleep(18)

        except NoSuchElementException:
            self.stdout.write("No next page")

        return

    def create_driver(self):
        self.stdout.write("Creating new driver...")

        download_dir = "/tmp/certificates"

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
                "download.default_directory": download_dir,  # Définir le dossier de téléchargement
                "download.prompt_for_download": False,  # Désactiver les pop-ups de confirmation de téléchargement
                "download.directory_upgrade": True,  # Mettre à jour le dossier de téléchargement si nécessaire
                "plugins.always_open_pdf_externally": True,  # Ouvrir les fichiers PDF directement (ne pas les ouvrir dans Chrome)
            },
        )

        driver = uc.Chrome(options=options)
        self.stdout.write("Driver ready")
        return driver

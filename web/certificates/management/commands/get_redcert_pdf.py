import html
import os
import re
import shutil
import time
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError

from core.models import GenericCertificate

DOWNLOAD_DIR = "/tmp/certificates"
FINAL_DIR = "/tmp/certificates/final"
URL = "https://redcert.eu/ZertifikateDatenAnzeige.aspx"
S3_FOLDER = "certificates/"
GRID_EVENT_TARGET = "ctl00$mainContentPlaceHolder$zertifikateDatenAnzeigeGridView"
PAGE_SIZE_CONTROL_ID = "ctl00_mainContentPlaceHolder_PaginationControl_NumberOfPageResultsLarge"
TOTAL_RESULTS_ID = "ctl00_mainContentPlaceHolder_PaginationControl_TotalNumberOfResults"


class Command(BaseCommand):
    help = "Download redcert certificates pdfs"

    def add_arguments(self, parser):
        parser.add_argument("--ids", type=str, help="Download specific certificates")
        parser.add_argument("--no-pdf", action="store_true", help="Download certificates without pdf")
        parser.add_argument("--exclude-ids", type=str, help="Exclude specific certificates by ids")
        parser.add_argument("--size", type=int, default=100, help="Number of certificates to search")

    def handle(self, *args, **options):
        start_time = time.time()
        self.create_directories()
        self.client = RedcertClient()

        certificates = None
        if options["ids"]:
            certificates = self.certificates_with_ids(options["ids"])
        elif options["no_pdf"]:
            certificates = self.certificates_without_pdf(options["exclude_ids"], options["size"])

        try:
            if certificates is not None:
                certificates_to_update = self.get_pdf_for_specific_certificates(certificates)
            else:
                certificates_to_update = self.get_all_certificates(start_time)
        except Exception as exc:
            raise CommandError(f"Error downloading REDcert PDFs: {exc}") from exc

        self.update_certificates(certificates_to_update)
        self.upload_all_certs_to_S3(len(certificates_to_update))

        self.stdout.write(f"Time spent: {time.time() - start_time:.2f} seconds")
        self.stdout.write(self.style.SUCCESS("Script executed successfully"))

    def create_directories(self):
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        os.makedirs(FINAL_DIR, exist_ok=True)

    def certificates_without_pdf(self, exclude_ids=None, size=100):
        excluded = exclude_ids.split(",") if exclude_ids else []
        queryset = GenericCertificate.objects.filter(
            certificate_type=GenericCertificate.REDCERT,
            download_link__isnull=True,
            valid_until__gte=time.strftime("%Y-%m-%d"),
        )
        if excluded:
            queryset = queryset.exclude(certificate_id__in=excluded)
        return queryset.order_by("-valid_until")[:size]

    def certificates_with_ids(self, certificate_ids):
        return GenericCertificate.objects.filter(certificate_id__in=certificate_ids.split(","))

    def get_pdf_for_specific_certificates(self, certificates):
        self.stdout.write("Searching for certificate with ids %s" % [c.certificate_id for c in certificates])

        certificates_to_update = []
        total = len(certificates)

        for i, certificate in enumerate(certificates):
            self.stdout.write(f"{i + 1}/{total}: {certificate.certificate_id}")
            page_html = self.client.search(certificate_id=certificate.certificate_id)
            rows = extract_rows(page_html)

            if not rows:
                self.stdout.write("No results found for certificate %s" % certificate.certificate_id)
                continue

            matching_row = next((row for row in rows if row.certificate_id == certificate.certificate_id), rows[0])

            try:
                self.download_certificate(page_html, matching_row, certificate)
            except NoDocumentError:
                self.stdout.write("No PDF found for certificate %s" % certificate.certificate_id)
            else:
                certificates_to_update.append(certificate)

        return certificates_to_update

    def get_all_certificates(self, start_time):
        self.stdout.write("No id provided, downloading all certificates")

        page_html = self.client.search(only_valid=True)
        page_html = self.client.set_page_size_to_100(page_html)

        certificates = GenericCertificate.objects.filter(
            certificate_type=GenericCertificate.REDCERT,
            valid_until__gte=time.strftime("%Y-%m-%d"),
        )
        certificate_ids = set(certificates.values_list("certificate_id", flat=True))

        nb_pdf_downloaded = 0
        nb_skipped = 0
        total_results = parse_total_results(page_html)
        max_pages = max(1, (total_results - 1) // 100 + 1)
        certificates_to_update = []

        self.stdout.write(f"{max_pages} pages")

        current_page_html = page_html
        for page_number in range(1, max_pages + 1):
            if page_number > 1:
                self.stdout.write(f"--> Going to page {page_number}")
                current_page_html = self.client.go_to_page(current_page_html, page_number)

            rows = extract_rows(current_page_html)
            nb_pdf_downloaded, nb_skipped, certificates_to_add = self.download_certificates(
                current_page_html,
                rows=rows,
                certificates=certificates,
                certificate_ids=certificate_ids,
                nb_pdf_downloaded=nb_pdf_downloaded,
                nb_skipped=nb_skipped,
            )
            certificates_to_update.extend(certificates_to_add)

            self.stdout.write(f"Time spent: {time.time() - start_time:.2f} seconds")
            self.stdout.write(f"Downloaded {nb_pdf_downloaded} pdfs")
            self.stdout.write(f"Skipped {nb_skipped} pdfs")

        self.stdout.write(f"TOTAL Downloaded {nb_pdf_downloaded} pdfs")
        self.stdout.write(f"TOTAL Skipped {nb_skipped} pdfs")

        return certificates_to_update

    def download_certificates(self, page_html, **kwargs):
        certificates = kwargs["certificates"]
        certificate_ids = kwargs["certificate_ids"]
        certificates_to_update = []

        for i, row in enumerate(kwargs["rows"]):
            redcert_id = row.certificate_id
            self.stdout.write(f"{i + 1}/{len(kwargs['rows'])}: {redcert_id}")

            if redcert_id not in certificate_ids:
                self.stdout.write("Skipping certificate %s" % redcert_id)
                kwargs["nb_skipped"] += 1
                continue

            certificate = certificates.filter(certificate_id=redcert_id).first()

            try:
                self.download_certificate(page_html, row, certificate)
                kwargs["nb_pdf_downloaded"] += 1
            except NoDocumentError:
                self.stdout.write("No PDF found for certificate %s" % redcert_id)
                kwargs["nb_skipped"] += 1
            else:
                certificates_to_update.append(certificate)

        return kwargs["nb_pdf_downloaded"], kwargs["nb_skipped"], certificates_to_update

    def download_certificate(self, page_html, row, certificate):
        if not row.has_document:
            raise NoDocumentError

        content = self.client.trigger_pdf_download(page_html, row.row_index)
        final_path = os.path.join(FINAL_DIR, f"certificate_{certificate.certificate_id}.pdf")
        with open(final_path, "wb") as pdf_file:
            pdf_file.write(content)

    def update_certificates(self, certificates_to_update):
        self.stdout.write("Updating certificates download links...")
        try:
            for certificate in certificates_to_update:
                s3_path = f"{S3_FOLDER}certificate_{certificate.certificate_id}.pdf"
                certificate.download_link = default_storage.url(s3_path)

            GenericCertificate.objects.bulk_update(certificates_to_update, ["download_link"])
        except Exception as exc:
            raise CommandError(f"Error updating certificates: {exc}") from exc

    def upload_all_certs_to_S3(self, counter):
        self.stdout.write(f"Transferring {counter} files to S3...")

        for idx, file_name in enumerate(os.listdir(FINAL_DIR)):
            local_file_path = os.path.join(FINAL_DIR, file_name)

            if os.path.isfile(local_file_path):
                s3_path = f"{S3_FOLDER}{file_name}"

                with open(local_file_path, "rb") as stored_file:
                    default_storage.save(s3_path, stored_file)

                self.stdout.write(f"\r{idx + 1}/{counter}", ending="")

        shutil.rmtree(DOWNLOAD_DIR)

        self.stdout.write("\n")
        self.stdout.write("All files transferred to S3")


class NoDocumentError(Exception):
    pass


@dataclass
class ResultRow:
    row_index: int
    certificate_id: str
    has_document: bool


class RedcertClient:
    def __init__(self, timeout=30.0):
        self.session = requests.Session()
        self.timeout = timeout

    def fetch_page(self):
        response = self.session.get(URL, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    def post(self, payload, allow_redirects=True):
        response = self.session.post(URL, data=payload, timeout=self.timeout, allow_redirects=allow_redirects)
        response.raise_for_status()
        return response

    def search(self, certificate_id="", only_valid=False):
        page_html = self.fetch_page()
        payload = extract_hidden_fields(page_html) | extract_default_search_form(page_html)
        payload.update(
            {
                "__EVENTTARGET": "",
                "__EVENTARGUMENT": "",
                "ctl00$mainContentPlaceHolder$zertifikatIdentifikatorTextBox": certificate_id,
                "ctl00$mainContentPlaceHolder$zertifikatsInhaberNameTextBox": "",
                "ctl00$mainContentPlaceHolder$zertifizierungsstellenNameTextBox": "",
                "ctl00$mainContentPlaceHolder$searchTypDEDropDownList": "%",
                "ctl00$mainContentPlaceHolder$searchLandDEDropDownList": "",
                "ctl00$mainContentPlaceHolder$searchStatusDELocalizedDropDownList": "1" if only_valid else "",
                "ctl00$mainContentPlaceHolder$SearchButton": "Suche starten",
            }
        )
        return self.post(payload).text

    def trigger_postback(self, page_html, *, element_id=None, input_value=None):
        target, argument = extract_postback(page_html, element_id=element_id, input_value=input_value)
        payload = extract_hidden_fields(page_html) | extract_default_search_form(page_html)
        payload.update(
            {
                "__EVENTTARGET": target,
                "__EVENTARGUMENT": argument,
            }
        )
        return self.post(payload).text

    def set_page_size_to_100(self, page_html):
        try:
            return self.trigger_postback(page_html, element_id=PAGE_SIZE_CONTROL_ID)
        except RuntimeError:
            return page_html

    def go_to_page(self, page_html, page_number):
        return self.trigger_postback(page_html, input_value=str(page_number))

    def trigger_pdf_download(self, page_html, row_index):
        payload = extract_hidden_fields(page_html) | extract_default_search_form(page_html)
        payload.update(
            {
                "__EVENTTARGET": GRID_EVENT_TARGET,
                "__EVENTARGUMENT": f"SelectedPDF${row_index}",
            }
        )
        response = self.post(payload, allow_redirects=False)
        location = response.headers.get("location")
        if response.status_code != 302 or not location:
            raise RuntimeError(f"Expected a redirect to the file download endpoint, got {response.status_code}")

        download_response = self.session.get(urljoin(URL, location), timeout=self.timeout)
        download_response.raise_for_status()

        content_type = download_response.headers.get("content-type", "")
        if "application/pdf" not in content_type.lower():
            raise RuntimeError(f"Unexpected content type: {content_type or 'missing'}")

        return download_response.content


def decode(value):
    value = html.unescape(value)
    value = re.sub(r"<[^>]+>", "", value)
    value = value.replace("\xa0", " ")
    return re.sub(r"\s+", " ", value).strip()


def extract_hidden_fields(page_html):
    fields = {}
    for name in (
        "__VIEWSTATE",
        "__VIEWSTATEGENERATOR",
        "__VIEWSTATEENCRYPTED",
        "__EVENTVALIDATION",
    ):
        match = re.search(rf'name="{re.escape(name)}"[^>]*value="([^"]*)"', page_html)
        if not match:
            raise RuntimeError(f"Missing hidden field: {name}")
        fields[name] = html.unescape(match.group(1))
    return fields


def extract_default_search_form(page_html):
    form_values = {
        "ctl00$mainContentPlaceHolder$zertifikatIdentifikatorTextBox": "",
        "ctl00$mainContentPlaceHolder$zertifikatsInhaberNameTextBox": "",
        "ctl00$mainContentPlaceHolder$zertifizierungsstellenNameTextBox": "",
        "ctl00$mainContentPlaceHolder$searchTypDEDropDownList": "%",
        "ctl00$mainContentPlaceHolder$firmenAnschriftPLZTextBox": "",
        "ctl00$mainContentPlaceHolder$OrtTextBox": "",
        "ctl00$mainContentPlaceHolder$searchLandDEDropDownList": "",
        "ctl00$mainContentPlaceHolder$searchStatusDELocalizedDropDownList": "",
    }

    for name in form_values:
        input_match = re.search(
            rf'name="{re.escape(name)}"[^>]*value="([^"]*)"',
            page_html,
            re.IGNORECASE,
        )
        if input_match:
            form_values[name] = html.unescape(input_match.group(1))
            continue

        option_match = re.search(
            rf'<select[^>]*name="{re.escape(name)}"[^>]*>.*?<option[^>]*selected="selected"[^>]*value="([^"]*)"',
            page_html,
            re.IGNORECASE | re.DOTALL,
        )
        if option_match:
            form_values[name] = html.unescape(option_match.group(1))

    return form_values


def extract_rows(page_html):
    pattern = re.compile(
        r"Selected\$(?P<row>\d+).*?</td>\s*<td>(?P<status>.*?)</td>\s*<td>(?P<cert_id>.*?)</td>"
        r"\s*<td>(?P<holder>.*?)</td>\s*<td>(?P<valid_from>.*?)</td>\s*<td>(?P<valid_to>.*?)</td>"
        r"\s*<td>(?P<certified_as>.*?)</td>\s*<td>(?P<biomass>.*?)</td>\s*<td>(?P<body>.*?)</td>"
        r"\s*<td>(?P<type>.*?)</td>\s*<td[^>]*>(?P<documentation>.*?)</td>",
        re.DOTALL,
    )
    rows = []
    for match in pattern.finditer(page_html):
        documentation_html = match.group("documentation")
        rows.append(
            ResultRow(
                row_index=int(match.group("row")),
                certificate_id=decode(match.group("cert_id")),
                has_document="SelectedPDF$" in documentation_html,
            )
        )
    return rows


def extract_postback(page_html, *, element_id=None, input_value=None):
    if element_id:
        patterns = [
            rf'<[^>]*id="{re.escape(element_id)}"[^>]*(?:onclick|href)="javascript:__doPostBack\(\'([^\']*)\',\'([^\']*)\'\)',
            rf'<[^>]*(?:onclick|href)="javascript:__doPostBack\(\'([^\']*)\',\'([^\']*)\'\)"[^>]*id="{re.escape(element_id)}"',
        ]
        for pattern in patterns:
            match = re.search(pattern, page_html, re.IGNORECASE)
            if match:
                return match.group(1), match.group(2)

    if input_value:
        patterns = [
            rf'<[^>]*value="{re.escape(input_value)}"[^>]*(?:onclick|href)="javascript:__doPostBack\(\'([^\']*)\',\'([^\']*)\'\)',
            rf'<[^>]*(?:onclick|href)="javascript:__doPostBack\(\'([^\']*)\',\'([^\']*)\'\)"[^>]*value="{re.escape(input_value)}"',
        ]
        for pattern in patterns:
            match = re.search(pattern, page_html, re.IGNORECASE)
            if match:
                return match.group(1), match.group(2)

    raise RuntimeError("Could not find expected postback control in REDcert page")


def parse_total_results(page_html):
    match = re.search(
        rf'id="{re.escape(TOTAL_RESULTS_ID)}"[^>]*>([^<]+)<',
        page_html,
        re.IGNORECASE,
    )
    if not match:
        raise RuntimeError("Could not determine REDcert total number of results")

    digits = re.search(r"(\d+)", decode(match.group(1)))
    if not digits:
        raise RuntimeError("Could not parse REDcert total number of results")

    return int(digits.group(1))

import tempfile
from datetime import date, timedelta
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from certificates.management.commands import get_redcert_pdf as command_module
from core.models import GenericCertificate
from transactions.factories.certificate import GenericCertificateFactory


class FakeResponse:
    def __init__(self, *, text="", content=b"", status_code=200, headers=None):
        self.text = text
        self.content = content
        self.status_code = status_code
        self.headers = headers or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self, *, get_responses=None, post_responses=None):
        self.get_responses = list(get_responses or [])
        self.post_responses = list(post_responses or [])
        self.get_calls = []
        self.post_calls = []

    def get(self, url, timeout):
        self.get_calls.append({"url": url, "timeout": timeout})
        if not self.get_responses:
            raise AssertionError("Unexpected GET call")
        return self.get_responses.pop(0)

    def post(self, url, data, timeout, allow_redirects=True):
        self.post_calls.append(
            {
                "url": url,
                "data": data,
                "timeout": timeout,
                "allow_redirects": allow_redirects,
            }
        )
        if not self.post_responses:
            raise AssertionError("Unexpected POST call")
        return self.post_responses.pop(0)


class FakeStorage:
    def __init__(self):
        self.saved = []

    def save(self, path, stored_file):
        self.saved.append((path, stored_file.read()))
        return path

    def url(self, path):
        return f"https://storage.test/{path}"


def render_hidden_fields():
    return """
        <input type="hidden" name="__VIEWSTATE" value="viewstate" />
        <input type="hidden" name="__VIEWSTATEGENERATOR" value="generator" />
        <input type="hidden" name="__VIEWSTATEENCRYPTED" value="" />
        <input type="hidden" name="__EVENTVALIDATION" value="eventvalidation" />
    """


def render_search_form():
    return """
        <input name="ctl00$mainContentPlaceHolder$zertifikatIdentifikatorTextBox" value="" />
        <input name="ctl00$mainContentPlaceHolder$zertifikatsInhaberNameTextBox" value="" />
        <input name="ctl00$mainContentPlaceHolder$zertifizierungsstellenNameTextBox" value="" />
        <input name="ctl00$mainContentPlaceHolder$firmenAnschriftPLZTextBox" value="" />
        <input name="ctl00$mainContentPlaceHolder$OrtTextBox" value="" />
        <select name="ctl00$mainContentPlaceHolder$searchTypDEDropDownList">
            <option selected="selected" value="%">All</option>
        </select>
        <select name="ctl00$mainContentPlaceHolder$searchLandDEDropDownList">
            <option selected="selected" value="">All</option>
        </select>
        <select name="ctl00$mainContentPlaceHolder$searchStatusDELocalizedDropDownList">
            <option selected="selected" value="">All</option>
        </select>
    """


def render_row(row_index, certificate_id, has_document=True):
    documentation = (
        f"<input type=\"button\" onclick=\"javascript:__doPostBack('{command_module.GRID_EVENT_TARGET}','SelectedPDF${row_index}')\" />"  # noqa: E501
        if has_document
        else ""
    )
    return f"""
        <tr>
            <td>
                <input type="button" onclick="javascript:__doPostBack('{command_module.GRID_EVENT_TARGET}','Selected${row_index}')" />
            </td>
            <td>Valid</td>
            <td>{certificate_id}</td>
            <td>Holder</td>
            <td>2025-01-01</td>
            <td>2026-01-01</td>
            <td>Trader</td>
            <td>Biomass</td>
            <td>Body</td>
            <td>Type</td>
            <td class="lastColumns">{documentation}</td>
        </tr>
    """  # noqa: E501


def render_results_page(*, rows, total_results=None, page_size_control=False, page_buttons=None):
    controls = []
    if page_size_control:
        controls.append(
            f"""
            <input
                id="{command_module.PAGE_SIZE_CONTROL_ID}"
                onclick="javascript:__doPostBack('pager','size100')"
            />
            """
        )
    for page_number in page_buttons or []:
        controls.append(
            f"<input value=\"{page_number}\" onclick=\"javascript:__doPostBack('pager','page${page_number}')\" />"
        )

    total = (
        f'<span id="{command_module.TOTAL_RESULTS_ID}">{total_results} results</span>' if total_results is not None else ""
    )

    return f"""
        <html>
            <body>
                {render_hidden_fields()}
                {render_search_form()}
                {total}
                {''.join(controls)}
                <table>
                    {''.join(rows)}
                </table>
            </body>
        </html>
    """


class GetRedcertPdfCommandTest(TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.download_dir = f"{self.tempdir.name}/downloads"
        self.final_dir = f"{self.download_dir}/final"
        self.storage = FakeStorage()

    def tearDown(self):
        self.tempdir.cleanup()

    def make_certificate(self, certificate_id, *, download_link=None, valid_until=None):
        return GenericCertificateFactory.create(
            certificate_id=certificate_id,
            certificate_type=GenericCertificate.REDCERT,
            download_link=download_link,
            valid_until=valid_until or (date.today() + timedelta(days=30)),
        )

    def run_command(self, *args, session):
        with (
            patch.object(command_module, "DOWNLOAD_DIR", self.download_dir),
            patch.object(command_module, "FINAL_DIR", self.final_dir),
            patch.object(command_module, "default_storage", self.storage),
            patch.object(command_module.requests, "Session", return_value=session),
        ):
            call_command("get_redcert_pdf", *args, stdout=StringIO())

    def test_ids_downloads_matching_certificate_and_updates_link(self):
        certificate = self.make_certificate("RC-001", download_link=None)
        session = FakeSession(
            get_responses=[
                FakeResponse(text=render_results_page(rows=[])),
                FakeResponse(content=b"%PDF-1.4", headers={"content-type": "application/pdf"}),
            ],
            post_responses=[
                FakeResponse(text=render_results_page(rows=[render_row(0, "RC-001")])),
                FakeResponse(status_code=302, headers={"location": "/pdfs/RC-001.pdf"}),
            ],
        )

        self.run_command("--ids=RC-001", session=session)

        certificate.refresh_from_db()
        self.assertEqual(certificate.download_link, "https://storage.test/certificates/certificate_RC-001.pdf")
        self.assertEqual(
            self.storage.saved,
            [("certificates/certificate_RC-001.pdf", b"%PDF-1.4")],
        )
        self.assertEqual(
            session.post_calls[0]["data"]["ctl00$mainContentPlaceHolder$zertifikatIdentifikatorTextBox"],
            "RC-001",
        )
        self.assertFalse(os_path_exists(self.download_dir))

    def test_ids_skips_certificate_when_no_search_result(self):
        certificate = self.make_certificate("RC-404", download_link=None)
        session = FakeSession(
            get_responses=[FakeResponse(text=render_results_page(rows=[]))],
            post_responses=[FakeResponse(text=render_results_page(rows=[]))],
        )

        self.run_command("--ids=RC-404", session=session)

        certificate.refresh_from_db()
        self.assertIsNone(certificate.download_link)
        self.assertEqual(self.storage.saved, [])

    def test_ids_skips_certificate_when_result_has_no_pdf(self):
        certificate = self.make_certificate("RC-NO-PDF", download_link=None)
        session = FakeSession(
            get_responses=[FakeResponse(text=render_results_page(rows=[]))],
            post_responses=[FakeResponse(text=render_results_page(rows=[render_row(0, "RC-NO-PDF", has_document=False)]))],
        )

        self.run_command("--ids=RC-NO-PDF", session=session)

        certificate.refresh_from_db()
        self.assertIsNone(certificate.download_link)
        self.assertEqual(self.storage.saved, [])

    def test_no_pdf_respects_size_and_excluded_ids(self):
        excluded = self.make_certificate("RC-EXCLUDED", download_link=None, valid_until=date.today() + timedelta(days=10))
        selected = self.make_certificate("RC-SELECTED", download_link=None, valid_until=date.today() + timedelta(days=20))
        self.make_certificate("RC-IGNORED", download_link=None, valid_until=date.today() + timedelta(days=5))

        session = FakeSession(
            get_responses=[
                FakeResponse(text=render_results_page(rows=[])),
                FakeResponse(content=b"%PDF-1.4", headers={"content-type": "application/pdf"}),
            ],
            post_responses=[
                FakeResponse(text=render_results_page(rows=[render_row(0, "RC-SELECTED")])),
                FakeResponse(status_code=302, headers={"location": "/pdfs/RC-SELECTED.pdf"}),
            ],
        )

        self.run_command("--no-pdf", "--exclude-ids=RC-EXCLUDED", "--size=1", session=session)

        excluded.refresh_from_db()
        selected.refresh_from_db()
        self.assertIsNone(excluded.download_link)
        self.assertEqual(selected.download_link, "https://storage.test/certificates/certificate_RC-SELECTED.pdf")
        self.assertEqual(
            session.post_calls[0]["data"]["ctl00$mainContentPlaceHolder$zertifikatIdentifikatorTextBox"],
            "RC-SELECTED",
        )

    def test_default_run_processes_paginated_results_and_skips_unknown_certificates(self):
        known_1 = self.make_certificate("RC-KNOWN-1", download_link=None)
        known_2 = self.make_certificate("RC-KNOWN-2", download_link=None)

        session = FakeSession(
            get_responses=[
                FakeResponse(text=render_results_page(rows=[])),
                FakeResponse(content=b"%PDF-1.4 known1", headers={"content-type": "application/pdf"}),
                FakeResponse(content=b"%PDF-1.4 known2", headers={"content-type": "application/pdf"}),
            ],
            post_responses=[
                FakeResponse(
                    text=render_results_page(
                        rows=[render_row(0, "RC-KNOWN-1"), render_row(1, "RC-UNKNOWN")],
                        total_results=120,
                        page_size_control=True,
                    )
                ),
                FakeResponse(
                    text=render_results_page(
                        rows=[render_row(0, "RC-KNOWN-1"), render_row(1, "RC-UNKNOWN")],
                        total_results=120,
                        page_buttons=[2],
                    )
                ),
                FakeResponse(status_code=302, headers={"location": "/pdfs/RC-KNOWN-1.pdf"}),
                FakeResponse(text=render_results_page(rows=[render_row(0, "RC-KNOWN-2")], total_results=120)),
                FakeResponse(status_code=302, headers={"location": "/pdfs/RC-KNOWN-2.pdf"}),
            ],
        )

        self.run_command(session=session)

        known_1.refresh_from_db()
        known_2.refresh_from_db()
        self.assertEqual(known_1.download_link, "https://storage.test/certificates/certificate_RC-KNOWN-1.pdf")
        self.assertEqual(known_2.download_link, "https://storage.test/certificates/certificate_RC-KNOWN-2.pdf")
        self.assertCountEqual(
            self.storage.saved,
            [
                ("certificates/certificate_RC-KNOWN-1.pdf", b"%PDF-1.4 known1"),
                ("certificates/certificate_RC-KNOWN-2.pdf", b"%PDF-1.4 known2"),
            ],
        )
        self.assertEqual(
            session.post_calls[0]["data"]["ctl00$mainContentPlaceHolder$searchStatusDELocalizedDropDownList"],
            "1",
        )
        self.assertFalse(os_path_exists(self.download_dir))

    def test_malformed_response_raises_command_error(self):
        self.make_certificate("RC-BROKEN", download_link=None)
        session = FakeSession(
            get_responses=[FakeResponse(text="<html></html>")],
            post_responses=[],
        )

        with self.assertRaises(CommandError):
            self.run_command("--ids=RC-BROKEN", session=session)


def os_path_exists(path):
    try:
        import os

        return os.path.exists(path)
    except OSError:
        return False

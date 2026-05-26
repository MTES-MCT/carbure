from datetime import date, timedelta
from io import StringIO
from unittest.mock import patch

import requests
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils import timezone

from core.management.commands import import_iscc_certificates as command_module
from core.models import GenericCertificate
from transactions.factories.certificate import GenericCertificateFactory


class FakeResponse:
    def __init__(self, payload=None, *, status_code=200, json_error=None):
        self.payload = payload
        self.status_code = status_code
        self.json_error = json_error

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        if self.json_error:
            raise self.json_error
        return self.payload


def api_payload(html, *, total_count=1, max_pages=1, success=True):
    return {
        "success": success,
        "data": {
            "data": {
                "html": html,
                "totalCount": total_count,
                "maxPages": max_pages,
            }
        },
    }


def render_certificate_card(
    certificate_id="EU-ISCC-Cert-FR123-0001",
    holder_title="Example Biofuels SAS, 1 rue Test, 75000 Paris, France",
    dates="05.05.26 – 04.05.27",
    scope="Trader",
    raw_material="Used cooking oil (UCO)",
    products="Biodiesel",
    issuer="Example Certification Body",
    issuer_title=None,
    certificate_link="https://hub.iscc-system.org/FileHandler/download/certificateFile/example",
):
    link = (
        f"""
        <a href="{certificate_link}" target="_blank" class="custom-button icon small">
            Certificate
        </a>
        """
        if certificate_link
        else ""
    )

    return f"""
    <div class="is-certificate">
        <div class="is-certificate-head">
            <div class="is-certificate-head-top">
                <div>
                    <div class="tag">{certificate_id}</div>
                    <div class="date smalltext">{dates}</div>
                </div>
                <h3 class="h4">
                    <span title="{holder_title}">Example Biofuels SAS, Paris, France</span>
                </h3>
            </div>
        </div>
        <div class="is-certificate-fold">
            <div class="is-certificate-fold-item">
                <p class="title smalltext">Scope</p>
                <p>{scope}</p>
            </div>
            <div class="is-certificate-fold-item">
                <p class="title smalltext">Raw Material</p>
                <p>{raw_material}</p>
            </div>
            <div class="is-certificate-fold-item">
                <p class="title smalltext">Products</p>
                <p>{products}</p>
            </div>
            <div class="is-certificate-fold-item">
                <p class="title smalltext">Processing Unit Type</p>
                <p>Food processing plant</p>
            </div>
            <div class="is-certificate-fold-item">
                <p class="title smalltext">Issuing CB</p>
                <p>{render_titled_value(issuer, issuer_title)}</p>
            </div>
        </div>
        <div class="corner">
            <a href="https://hub.iscc-system.org/FileHandler/download/summaryAuditReportFile/example">Audit Report</a>
            {link}
        </div>
    </div>
    """


def render_titled_value(value, title):
    if not title:
        return value

    return f'<span title="{title}">{value}</span>'


class ImportISCCCertificatesCommandTest(TestCase):
    def run_command(self, *args):
        stdout = StringIO()
        with patch.object(command_module, "fetch_scope_definitions", return_value={}):
            call_command("import_iscc_certificates", *args, stdout=stdout, stderr=StringIO())
        return stdout.getvalue()

    def test_import_creates_certificate_from_valid_card(self):
        with patch.object(
            command_module.requests,
            "post",
            return_value=FakeResponse(api_payload(render_certificate_card())),
        ) as post:
            output = self.run_command("--statuses", "valid")

        certificate = GenericCertificate.objects.get(certificate_id="EU-ISCC-Cert-FR123-0001")
        self.assertEqual(certificate.certificate_type, GenericCertificate.ISCC)
        self.assertEqual(certificate.certificate_holder, "Example Biofuels SAS")
        self.assertEqual(certificate.address, "Example Biofuels SAS, 1 rue Test, 75000 Paris, France")
        self.assertEqual(certificate.valid_from, date(2026, 5, 5))
        self.assertEqual(certificate.valid_until, date(2027, 5, 4))
        self.assertEqual(certificate.certificate_issuer, "Example Certification Body")
        self.assertEqual(certificate.scope, "Trader")
        self.assertEqual(certificate.input, {"raw_material": "Used cooking oil (UCO)"})
        self.assertEqual(certificate.output, {"products": "Biodiesel"})
        self.assertEqual(
            certificate.download_link,
            "https://hub.iscc-system.org/FileHandler/download/certificateFile/example",
        )
        self.assertEqual(certificate.status, GenericCertificate.VALID)
        self.assertIn("> valid: 0 updated, 1 created", output)
        self.assertEqual(post.call_args.kwargs["json"]["filters"], {"status": ["valid"]})
        self.assertEqual(post.call_args.kwargs["json"]["count"], command_module.ISCC_PAGE_SIZE)
        self.assertEqual(post.call_args.kwargs["json"]["page"], 1)
        self.assertEqual(post.call_args.kwargs["timeout"], 60)

    def test_import_sends_email_summary_when_requested(self):
        with (
            patch.object(
                command_module.requests,
                "post",
                return_value=FakeResponse(api_payload(render_certificate_card())),
            ),
            patch.object(command_module, "send_mail") as send_mail,
        ):
            self.run_command("--statuses", "valid", "--email")

        send_mail.assert_called_once()
        subject, body, from_email, recipients = send_mail.call_args.args[:4]
        self.assertEqual(subject, "Certificats ISCC - 1 chargés - 1 nouveaux")
        self.assertIn("Certificats chargés: 1", body)
        self.assertIn("Certificats créés: 1", body)
        self.assertIn("EU-ISCC-Cert-FR123-0001 - Example Biofuels SAS", body)
        self.assertTrue(from_email)
        self.assertEqual(recipients, ["carbure@beta.gouv.fr"])

    def test_import_expands_scope_abbreviations(self):
        html = render_certificate_card(scope="CP, TRS")
        certificates, errors = command_module.parse_certificates_html(
            html,
            GenericCertificate.VALID,
            scope_definitions={
                "CP": "Collecting Point",
                "TRS": "Trader with Storage",
            },
        )

        self.assertEqual(errors, [])
        self.assertEqual(certificates[0]["scope"], "Collecting Point, Trader with Storage")

    def test_import_prefers_issuer_title_attribute(self):
        html = render_certificate_card(
            issuer="Short Issuer",
            issuer_title="Long Issuer GmbH, Berlin, DE",
        )
        certificates, errors = command_module.parse_certificates_html(html, GenericCertificate.VALID)

        self.assertEqual(errors, [])
        self.assertEqual(certificates[0]["certificate_issuer"], "Long Issuer GmbH, Berlin, DE")

    def test_parse_scope_definitions_from_iscc_page_content(self):
        definitions = command_module.parse_scope_definitions(
            """
            <div class="wp-block-group__inner-container">
                <p><strong>CP</strong> = Collecting Point<br /></p>
                <p><strong>TRS =</strong> Trader with Storage<br /></p>
                <p><strong>PU</strong> = Processing Unit <span>with details</span><br /></p>
            </div>
            """
        )

        self.assertEqual(
            definitions,
            {
                "CP": "Collecting Point",
                "TRS": "Trader with Storage",
                "PU": "Processing Unit with details",
            },
        )

    def test_import_fetches_all_pages_for_status(self):
        responses = [
            FakeResponse(
                api_payload(
                    render_certificate_card(certificate_id="EU-ISCC-Cert-FR123-PAGE-1"),
                    total_count=2,
                    max_pages=2,
                )
            ),
            FakeResponse(
                api_payload(
                    render_certificate_card(certificate_id="EU-ISCC-Cert-FR123-PAGE-2"),
                    total_count=2,
                    max_pages=2,
                )
            ),
        ]

        with patch.object(command_module.requests, "post", side_effect=responses) as post:
            output = self.run_command("--statuses", "valid")

        self.assertTrue(GenericCertificate.objects.filter(certificate_id="EU-ISCC-Cert-FR123-PAGE-1").exists())
        self.assertTrue(GenericCertificate.objects.filter(certificate_id="EU-ISCC-Cert-FR123-PAGE-2").exists())
        self.assertEqual([call.kwargs["json"]["page"] for call in post.call_args_list], [1, 2])
        self.assertIn("> valid: parsed 2 certificates from 2 ISCC results across 2 pages", output)

    def test_latest_limits_imported_certificates_and_stops_fetching_pages(self):
        responses = [
            FakeResponse(
                api_payload(
                    render_certificate_card(certificate_id="EU-ISCC-Cert-FR123-LATEST-1")
                    + render_certificate_card(certificate_id="EU-ISCC-Cert-FR123-LATEST-2"),
                    total_count=400,
                    max_pages=2,
                )
            ),
            FakeResponse(
                api_payload(
                    render_certificate_card(certificate_id="EU-ISCC-Cert-FR123-LATEST-3"),
                    total_count=400,
                    max_pages=2,
                )
            ),
        ]

        with patch.object(command_module.requests, "post", side_effect=responses) as post:
            output = self.run_command("--statuses", "valid", "--latest", "1")

        self.assertTrue(GenericCertificate.objects.filter(certificate_id="EU-ISCC-Cert-FR123-LATEST-1").exists())
        self.assertFalse(GenericCertificate.objects.filter(certificate_id="EU-ISCC-Cert-FR123-LATEST-2").exists())
        self.assertFalse(GenericCertificate.objects.filter(certificate_id="EU-ISCC-Cert-FR123-LATEST-3").exists())
        self.assertEqual([call.kwargs["json"]["page"] for call in post.call_args_list], [1])
        self.assertIn("> valid: parsed 1 certificates from 400 ISCC results across 1 pages", output)

    def test_import_maps_each_iscc_status_to_django_status(self):
        responses = []
        for iscc_status in command_module.ISCC_STATUS_MAPPING:
            html = render_certificate_card(certificate_id=f"EU-ISCC-Cert-FR123-{iscc_status}")
            responses.append(FakeResponse(api_payload(html)))

        with patch.object(command_module.requests, "post", side_effect=responses) as post:
            self.run_command()

        for iscc_status, django_status in command_module.ISCC_STATUS_MAPPING.items():
            certificate = GenericCertificate.objects.get(certificate_id=f"EU-ISCC-Cert-FR123-{iscc_status}")
            self.assertEqual(certificate.status, django_status)

        requested_statuses = [call.kwargs["json"]["filters"]["status"][0] for call in post.call_args_list]
        self.assertEqual(requested_statuses, list(command_module.ISCC_STATUS_MAPPING.keys()))

    def test_import_updates_existing_certificate_and_status_update_date(self):
        yesterday = timezone.localdate() - timedelta(days=1)
        existing = GenericCertificateFactory.create(
            certificate_id="EU-ISCC-Cert-FR123-0001",
            certificate_type=GenericCertificate.ISCC,
            status=GenericCertificate.VALID,
            last_status_update=yesterday,
        )

        html = render_certificate_card(holder_title="Updated Holder SA, 2 rue Test, 69000 Lyon, France")
        with patch.object(command_module.requests, "post", return_value=FakeResponse(api_payload(html))):
            self.run_command("--statuses", "suspended")

        existing.refresh_from_db()
        self.assertEqual(existing.status, GenericCertificate.SUSPENDED)
        self.assertEqual(existing.certificate_holder, "Updated Holder SA")
        self.assertEqual(existing.last_status_update, timezone.localdate())

    def test_import_expires_only_pending_or_valid_saved_iscc_certificates_locally(self):
        yesterday = timezone.localdate() - timedelta(days=1)
        past_valid_iscc = GenericCertificateFactory.create(
            certificate_id="EU-ISCC-Cert-FR123-EXPIRED",
            certificate_type=GenericCertificate.ISCC,
            status=GenericCertificate.VALID,
            valid_until=yesterday,
            last_status_update=yesterday,
        )
        past_suspended_iscc = GenericCertificateFactory.create(
            certificate_type=GenericCertificate.ISCC,
            status=GenericCertificate.SUSPENDED,
            valid_until=yesterday,
            last_status_update=yesterday,
        )
        past_terminated_iscc = GenericCertificateFactory.create(
            certificate_type=GenericCertificate.ISCC,
            status=GenericCertificate.TERMINATED,
            valid_until=yesterday,
            last_status_update=yesterday,
        )
        past_withdrawn_iscc = GenericCertificateFactory.create(
            certificate_type=GenericCertificate.ISCC,
            status=GenericCertificate.WITHDRAWN,
            valid_until=yesterday,
            last_status_update=yesterday,
        )
        past_redcert = GenericCertificateFactory.create(
            certificate_type=GenericCertificate.REDCERT,
            status=GenericCertificate.VALID,
            valid_until=yesterday,
            last_status_update=yesterday,
        )

        with patch.object(
            command_module.requests,
            "post",
            return_value=FakeResponse(api_payload(render_certificate_card())),
        ):
            output = self.run_command("--statuses", "valid")

        past_valid_iscc.refresh_from_db()
        past_suspended_iscc.refresh_from_db()
        past_terminated_iscc.refresh_from_db()
        past_withdrawn_iscc.refresh_from_db()
        past_redcert.refresh_from_db()
        self.assertEqual(past_valid_iscc.status, GenericCertificate.EXPIRED)
        self.assertEqual(past_valid_iscc.last_status_update, timezone.localdate())
        self.assertEqual(past_suspended_iscc.status, GenericCertificate.SUSPENDED)
        self.assertEqual(past_terminated_iscc.status, GenericCertificate.TERMINATED)
        self.assertEqual(past_withdrawn_iscc.status, GenericCertificate.WITHDRAWN)
        self.assertEqual(past_redcert.status, GenericCertificate.VALID)
        self.assertEqual(past_redcert.last_status_update, yesterday)
        self.assertIn("> expired: 1 existing ISCC certificates marked as expired", output)

    def test_dry_run_does_not_write_to_database(self):
        certificate_id = "EU-ISCC-Cert-FR123-DRY-RUN"
        with patch.object(
            command_module.requests,
            "post",
            return_value=FakeResponse(api_payload(render_certificate_card(certificate_id=certificate_id))),
        ):
            output = self.run_command("--statuses", "valid", "--dry-run")

        self.assertFalse(GenericCertificate.objects.filter(certificate_id=certificate_id).exists())
        self.assertIn("> Dry run complete: 1 parsed, 0 skipped", output)

    def test_dry_run_does_not_expire_saved_iscc_certificates(self):
        yesterday = timezone.localdate() - timedelta(days=1)
        certificate = GenericCertificateFactory.create(
            certificate_type=GenericCertificate.ISCC,
            status=GenericCertificate.VALID,
            valid_until=yesterday,
            last_status_update=yesterday,
        )

        with patch.object(
            command_module.requests,
            "post",
            return_value=FakeResponse(api_payload(render_certificate_card(certificate_id="EU-ISCC-Cert-FR123-DRY"))),
        ):
            output = self.run_command("--statuses", "valid", "--dry-run")

        certificate.refresh_from_db()
        self.assertEqual(certificate.status, GenericCertificate.VALID)
        self.assertEqual(certificate.last_status_update, yesterday)
        self.assertIn("> expired: 1 existing ISCC certificates marked as expired", output)

    def test_missing_optional_fields_do_not_crash(self):
        html = render_certificate_card(
            raw_material="",
            products="-",
            certificate_link=None,
        )
        with patch.object(command_module.requests, "post", return_value=FakeResponse(api_payload(html))):
            self.run_command("--statuses", "valid")

        certificate = GenericCertificate.objects.get(certificate_id="EU-ISCC-Cert-FR123-0001")
        self.assertEqual(certificate.input, {"raw_material": ""})
        self.assertEqual(certificate.output, {"products": ""})
        self.assertIsNone(certificate.download_link)

    def test_malformed_cards_are_skipped(self):
        html = render_certificate_card(certificate_id="") + render_certificate_card(certificate_id="VALID-CERT")
        with patch.object(command_module.requests, "post", return_value=FakeResponse(api_payload(html))):
            output = self.run_command("--statuses", "valid")

        self.assertEqual(GenericCertificate.objects.filter(certificate_id="VALID-CERT").count(), 1)
        self.assertTrue(GenericCertificate.objects.filter(certificate_id="VALID-CERT").exists())
        self.assertIn("skipped 1 malformed certificates", output)

    def test_http_failure_raises_command_error(self):
        with patch.object(command_module.requests, "post", return_value=FakeResponse(status_code=500)):
            with self.assertRaises(CommandError):
                self.run_command("--statuses", "valid")

    def test_unsuccessful_api_response_raises_command_error(self):
        with patch.object(
            command_module.requests,
            "post",
            return_value=FakeResponse(api_payload("", success=False)),
        ):
            with self.assertRaises(CommandError):
                self.run_command("--statuses", "valid")

    def test_invalid_latest_raises_command_error(self):
        with self.assertRaises(CommandError):
            self.run_command("--statuses", "valid", "--latest", "0")

from datetime import date
from io import StringIO
from unittest.mock import Mock, patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from core.management.commands import import_certifhy_certificates
from core.models import GenericCertificate

CERTIFICATE_HTML = """
<div class="js-cert-card">
  <div><span class="font-semibold">Certificate ID:</span><div>FAKE-CERTIFICATE-001</div></div>
  <div><span class="font-semibold">Certificate Holder:</span><div>Example Certificate Holder</div></div>
  <div><span class="font-semibold">Status:</span><div><span>Valid</span></div></div>
  <div><span class="font-semibold">Products:</span><div>Example Product</div></div>
  <div><span class="font-semibold">Scope:</span><div>Example Scope</div></div>
  <div><span class="font-semibold">Valid From:</span><div>01/02/2025</div></div>
  <div><span class="font-semibold">Valid Until:</span><div>31/01/2026</div></div>
  <div><span class="font-semibold">Issuing CB:</span><div>Example Certification Body</div></div>
  <a href="https://example.test/certificate.pdf">Certificate</a>
  <a href="https://example.test/audit.pdf">Audit Report</a>
</div>
"""


class ImportCertifhyCertificatesTest(TestCase):
    @patch.object(import_certifhy_certificates.requests, "get")
    def test_imports_certificates(self, get):
        response = Mock(text=CERTIFICATE_HTML)
        response.raise_for_status.return_value = None
        get.return_value = response

        stdout = StringIO()
        call_command("import_certifhy_certificates", stdout=stdout)

        certificate = GenericCertificate.objects.get(certificate_id="FAKE-CERTIFICATE-001")
        self.assertEqual(certificate.certificate_type, GenericCertificate.CERTIFHY)
        self.assertEqual(certificate.certificate_holder, "Example Certificate Holder")
        self.assertEqual(certificate.certificate_issuer, "Example Certification Body")
        self.assertEqual(certificate.valid_from, date(2025, 2, 1))
        self.assertEqual(certificate.valid_until, date(2026, 1, 31))
        self.assertEqual(certificate.status, GenericCertificate.VALID)
        self.assertEqual(certificate.scope, "Example Scope")
        self.assertEqual(certificate.output, {"products": "Example Product"})
        self.assertEqual(certificate.download_link, "https://example.test/certificate.pdf")
        self.assertIn("1 created, 0 updated", stdout.getvalue())

    def test_rejects_unknown_status(self):
        html = CERTIFICATE_HTML.replace(">Valid<", ">Revoked<")

        with self.assertRaisesMessage(CommandError, "unknown status: Revoked"):
            import_certifhy_certificates.parse_certificates(html)

    def test_rejects_page_without_certificates(self):
        with self.assertRaisesMessage(CommandError, "No CertifHy certificates found"):
            import_certifhy_certificates.parse_certificates("<html></html>")

from datetime import timedelta
from unittest import TestCase

from django.core.management import call_command
from django.utils import timezone

from core.models import GenericCertificate
from transactions.factories.certificate import GenericCertificateFactory


class UpdateCertificateStatusTest(TestCase):
    def test_update_expired_certificates(self):
        today = timezone.localdate()
        tomorrow = today + timedelta(days=1)
        yesterday = today - timedelta(days=1)
        future_year = today + timedelta(weeks=52)
        past_year = today - timedelta(weeks=52)

        # valid certificate
        valid_cert_1 = GenericCertificateFactory.create(
            valid_from=today,
            valid_until=future_year,
            last_status_update=yesterday,
        )

        valid_cert_2 = GenericCertificateFactory.create(
            valid_from=past_year,
            valid_until=today,
            last_status_update=yesterday,
        )

        # pending certificate
        pending_cert = GenericCertificateFactory.create(
            valid_from=tomorrow,
            valid_until=future_year,
            last_status_update=yesterday,
        )

        # expired certificate
        expired_cert = GenericCertificateFactory.create(
            valid_from=past_year,
            valid_until=yesterday,
            last_status_update=yesterday,
        )

        # other statuses
        suspended_cert = GenericCertificateFactory.create(
            status=GenericCertificate.SUSPENDED,
            valid_from=past_year,
            valid_until=future_year,
            last_status_update=yesterday,
        )
        withdrawn_cert = GenericCertificateFactory.create(
            status=GenericCertificate.WITHDRAWN,
            valid_from=past_year,
            valid_until=future_year,
            last_status_update=yesterday,
        )
        terminated_cert = GenericCertificateFactory.create(
            status=GenericCertificate.TERMINATED,
            valid_from=past_year,
            valid_until=future_year,
            last_status_update=yesterday,
        )

        call_command("update_certificate_status")

        valid_cert_1.refresh_from_db()
        valid_cert_2.refresh_from_db()
        pending_cert.refresh_from_db()
        expired_cert.refresh_from_db()
        suspended_cert.refresh_from_db()
        withdrawn_cert.refresh_from_db()
        terminated_cert.refresh_from_db()

        self.assertEqual(valid_cert_1.status, GenericCertificate.VALID)
        self.assertEqual(valid_cert_1.last_status_update, yesterday)

        self.assertEqual(valid_cert_2.status, GenericCertificate.VALID)
        self.assertEqual(valid_cert_2.last_status_update, yesterday)

        self.assertEqual(pending_cert.status, GenericCertificate.PENDING)
        self.assertEqual(pending_cert.last_status_update, today)  # updated

        self.assertEqual(expired_cert.status, GenericCertificate.EXPIRED)
        self.assertEqual(expired_cert.last_status_update, today)  # updated

        # certificates with other status are not affected
        self.assertEqual(suspended_cert.status, GenericCertificate.SUSPENDED)
        self.assertEqual(suspended_cert.last_status_update, yesterday)

        self.assertEqual(withdrawn_cert.status, GenericCertificate.WITHDRAWN)
        self.assertEqual(withdrawn_cert.last_status_update, yesterday)

        self.assertEqual(terminated_cert.status, GenericCertificate.TERMINATED)
        self.assertEqual(terminated_cert.last_status_update, yesterday)

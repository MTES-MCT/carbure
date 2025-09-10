from datetime import date

from django.test import TestCase
from django.urls import reverse
from matplotlib.dates import relativedelta

from core.models import Entity, GenericCertificate
from core.tests_utils import setup_current_user
from resources.factories.generic_certificate import GenericCertificateFactory


class SystemeNationalTest(TestCase):
    active_valid_until = date.today() + relativedelta(years=10)

    def setUp(self):
        self.entity = Entity.objects.create(name="TestEntity", entity_type=Entity.OPERATOR)
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, "RW")], True)

    def get_sn_certificates(self, query=""):
        url = reverse("resources-systeme-national")
        query_params = {"query": query} if query else {}
        response = self.client.get(url, query_params=query_params)
        return response.json()

    def test_list_sn_certificates(self):
        sn_cert: GenericCertificate = GenericCertificateFactory.create(
            certificate_type=GenericCertificate.SYSTEME_NATIONAL,
            valid_until=self.active_valid_until,
        )

        data = self.get_sn_certificates()

        self.assertEqual(
            data,
            [
                {
                    "certificate_id": sn_cert.certificate_id,
                    "certificate_type": GenericCertificate.SYSTEME_NATIONAL,
                    "certificate_holder": sn_cert.certificate_holder,
                    "certificate_issuer": sn_cert.certificate_issuer,
                    "address": sn_cert.address,
                    "valid_from": f"{sn_cert.valid_from:%Y-%m-%d}",
                    "valid_until": f"{sn_cert.valid_until:%Y-%m-%d}",
                    "download_link": sn_cert.download_link,
                    "scope": sn_cert.scope,
                    "input": sn_cert.input,
                    "output": sn_cert.output,
                }
            ],
        )

    def test_ignore_non_sn_certificates(self):
        GenericCertificateFactory.create(certificate_type=GenericCertificate.ISCC)
        data = self.get_sn_certificates()
        self.assertEqual(data, [])

    def test_list_only_active_sn_certificates(self):
        """
        Active certificates are the ones where their valid_from/valid_until timespan
        covers today's date.
        """

        today = date.today()

        active_cert = GenericCertificateFactory.create(
            certificate_type=GenericCertificate.SYSTEME_NATIONAL,
            valid_from=today - relativedelta(years=1),
            valid_until=today + relativedelta(years=1),
        )

        _expired_cert = GenericCertificateFactory.create(
            certificate_type=GenericCertificate.SYSTEME_NATIONAL,
            valid_from=today - relativedelta(years=2),
            valid_until=today - relativedelta(years=1),
        )

        data = self.get_sn_certificates()

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["certificate_id"], active_cert.certificate_id)

    def test_search_sn_certificates_by_certificate_id(self):
        _cert_a = GenericCertificateFactory.create(
            certificate_id="ABCD",
            certificate_type=GenericCertificate.SYSTEME_NATIONAL,
            valid_until=self.active_valid_until,
        )

        cert_b = GenericCertificateFactory.create(
            certificate_id="EFGH",
            certificate_type=GenericCertificate.SYSTEME_NATIONAL,
            valid_until=self.active_valid_until,
        )

        data = self.get_sn_certificates(query="FG")

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["certificate_id"], cert_b.certificate_id)

    def test_search_sn_certificates_by_certificate_holder(self):
        _cert_a = GenericCertificateFactory.create(
            certificate_id="ABCD",
            certificate_holder="Alice",
            certificate_type=GenericCertificate.SYSTEME_NATIONAL,
            valid_until=self.active_valid_until,
        )

        cert_b = GenericCertificateFactory.create(
            certificate_id="EFGH",
            certificate_holder="Bob",
            certificate_type=GenericCertificate.SYSTEME_NATIONAL,
            valid_until=self.active_valid_until,
        )

        data = self.get_sn_certificates(query="ob")

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["certificate_id"], cert_b.certificate_id)

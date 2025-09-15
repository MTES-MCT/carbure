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
        today = date.today()

        active_sn_cert: GenericCertificate = GenericCertificateFactory.create(
            certificate_type=GenericCertificate.SYSTEME_NATIONAL,
            valid_until=self.active_valid_until,
        )

        # the endpoint ignores any certificate that is not SYSTEME_NATIONAL
        _non_sn_cert = GenericCertificateFactory.create(
            certificate_type=GenericCertificate.ISCC,
        )

        # the endpoint ignores any certificate that isn't valid today
        _expired_sn_cert = GenericCertificateFactory.create(
            certificate_type=GenericCertificate.SYSTEME_NATIONAL,
            valid_from=today - relativedelta(years=2),
            valid_until=today - relativedelta(years=1),
        )

        data = self.get_sn_certificates()

        self.assertEqual(
            data,
            [
                {
                    "certificate_id": active_sn_cert.certificate_id,
                    "certificate_type": GenericCertificate.SYSTEME_NATIONAL,
                    "certificate_holder": active_sn_cert.certificate_holder,
                    "certificate_issuer": active_sn_cert.certificate_issuer,
                    "address": active_sn_cert.address,
                    "valid_from": f"{active_sn_cert.valid_from:%Y-%m-%d}",
                    "valid_until": f"{active_sn_cert.valid_until:%Y-%m-%d}",
                    "download_link": active_sn_cert.download_link,
                    "scope": active_sn_cert.scope,
                    "input": active_sn_cert.input,
                    "output": active_sn_cert.output,
                }
            ],
        )

    def test_search_sn_certificates_by_certificate_id(self):
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

        # match with certificate_id
        data_from_id = self.get_sn_certificates(query="FG")

        self.assertEqual(len(data_from_id), 1)
        self.assertEqual(data_from_id[0]["certificate_id"], cert_b.certificate_id)

        # match with certificate_holder
        data_from_holder = self.get_sn_certificates(query="ob")

        self.assertEqual(len(data_from_holder), 1)
        self.assertEqual(data_from_holder[0]["certificate_id"], cert_b.certificate_id)

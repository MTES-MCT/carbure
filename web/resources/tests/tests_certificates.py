import datetime

from django.test import TestCase
from django.urls import reverse

from core.tests_utils import setup_current_user
from transactions.factories.certificate import GenericCertificateFactory


class ResourcesTest(TestCase):
    def setUp(self):
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo")

    def test_certificates(self):
        GenericCertificateFactory(
            certificate_id="2024",
            valid_from=datetime.date(2024, 1, 1),
            valid_until=datetime.date(2024, 12, 31),
        )

        GenericCertificateFactory(
            certificate_id="2025",
            valid_from=datetime.date(2025, 1, 1),
            valid_until=datetime.date(2025, 12, 31),
        )

        data = self.client.get(reverse("resources-certificates"), query_params={"query": "2025"}).json()
        assert len(data) == 1
        assert data[0]["certificate_id"] == "2025"

        data = self.client.get(reverse("resources-certificates"), query_params={"date": "2024-06-01"}).json()
        assert len(data) == 1
        assert data[0]["certificate_id"] == "2024"

from django.test import TestCase
from django.urls import reverse

from core.models import Entity
from core.tests_utils import setup_current_user
from saf.factories import SafTicketFactory
from saf.models import SafTicket


class SafSnapshotTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/productionsites.json",
        "json/entities_sites.json",
    ]

    def setUp(self):
        self.entity = Entity.objects.filter(entity_type=Entity.OPERATOR)[0]
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, "ADMIN")])

        SafTicket.objects.all().delete()
        SafTicketFactory.create_batch(15, year=2022, client_id=self.entity.id, status=SafTicket.PENDING)
        SafTicketFactory.create_batch(10, year=2022, client_id=self.entity.id, status=SafTicket.ACCEPTED)
        SafTicketFactory.create_batch(5, year=2022, client_id=self.entity.id, status=SafTicket.REJECTED)

    def test_saf_snapshot_empty(self):
        response = self.client.get(reverse("saf-airline-snapshot"), {"entity_id": self.entity.id, "year": 2021})

        expected = {
            "tickets_pending": 0,
            "tickets_accepted": 0,
        }

        assert response.status_code == 200
        assert response.json()["data"] == expected

    def test_saf_snapshot(self):
        response = self.client.get(reverse("saf-airline-snapshot"), {"entity_id": self.entity.id, "year": 2022})

        expected = {
            "tickets_pending": 15,
            "tickets_accepted": 10,
        }

        assert response.status_code == 200
        assert response.json()["data"] == expected

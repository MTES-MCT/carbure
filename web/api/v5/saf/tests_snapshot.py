from django.test import TestCase
from django.urls import reverse


from api.v4.tests_utils import setup_current_user
from core.models import Entity
from saf.factories import SafTicketSourceFactory, SafTicketFactory
from saf.models import SafTicketSource, SafTicket


class SafSnapshotTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/productionsites.json",
    ]

    def setUp(self):
        self.entity = Entity.objects.filter(entity_type=Entity.OPERATOR)[0]
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, "ADMIN")])

        SafTicketSource.objects.all().delete()
        SafTicketSourceFactory.create_batch(10, year=2021, added_by_id=self.entity.id, assigned_volume=0)
        SafTicketSourceFactory.create_batch(10, year=2022, added_by_id=self.entity.id, assigned_volume=0)
        SafTicketSourceFactory.create_batch(20, year=2022, added_by_id=self.entity.id, total_volume=30000, assigned_volume=30000)  # fmt:skip

        SafTicket.objects.all().delete()
        SafTicketFactory.create_batch(15, year=2022, added_by_id=self.entity.id, status=SafTicket.PENDING)
        SafTicketFactory.create_batch(10, year=2022, added_by_id=self.entity.id, status=SafTicket.ACCEPTED)
        SafTicketFactory.create_batch(5, year=2022, added_by_id=self.entity.id, status=SafTicket.REJECTED)

    def test_saf_snapshot_simple(self):
        response = self.client.get(reverse("api-v5-saf-snapshot"), {"entity_id": self.entity.id, "year": 2021})

        expected = {
            "ticket_sources_available": 10,
            "ticket_sources_history": 0,
            "tickets": 0,
            "tickets_pending": 0,
            "tickets_rejected": 0,
            "tickets_accepted": 0,
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"], expected)
        response = self.client.get(reverse("api-v5-saf-snapshot"), {"entity_id": self.entity.id, "year": 2021})

    def test_saf_snapshot_complex(self):
        response = self.client.get(reverse("api-v5-saf-snapshot"), {"entity_id": self.entity.id, "year": 2022})

        expected = {
            "ticket_sources_available": 10,
            "ticket_sources_history": 20,
            "tickets": 30,
            "tickets_pending": 15,
            "tickets_accepted": 10,
            "tickets_rejected": 5,
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"], expected)

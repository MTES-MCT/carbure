from django.test import TestCase
from django.urls import reverse


from core.tests_utils import setup_current_user
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
        self.entity2 = Entity.objects.filter(entity_type=Entity.OPERATOR)[1]
        self.user = setup_current_user(
            self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, "ADMIN")]
        )

        SafTicketSource.objects.all().delete()
        SafTicketSourceFactory.create_batch(
            10, year=2021, added_by_id=self.entity.id, assigned_volume=0
        )
        SafTicketSourceFactory.create_batch(
            10, year=2022, added_by_id=self.entity.id, assigned_volume=0
        )
        SafTicketSourceFactory.create_batch(20, year=2022, added_by_id=self.entity.id, total_volume=30000, assigned_volume=30000)  # fmt:skip

        SafTicket.objects.all().delete()
        SafTicketFactory.create_batch(15, year=2022, supplier_id=self.entity.id, client_id=self.entity2.id, status=SafTicket.PENDING)  # fmt:skip
        SafTicketFactory.create_batch(10, year=2022, supplier_id=self.entity.id, client_id=self.entity2.id, status=SafTicket.ACCEPTED)  # fmt:skip
        SafTicketFactory.create_batch(5, year=2022, supplier_id=self.entity.id, client_id=self.entity2.id, status=SafTicket.REJECTED)  # fmt:skip

    def test_saf_snapshot_simple(self):
        response = self.client.get(
            reverse("saf-operator-snapshot"),
            {"entity_id": self.entity.id, "year": 2021},
        )

        expected = {
            "ticket_sources_available": 10,
            "ticket_sources_history": 0,
            "tickets_assigned": 0,
            "tickets_assigned_pending": 0,
            "tickets_assigned_rejected": 0,
            "tickets_assigned_accepted": 0,
            "tickets_received": 0,
            "tickets_received_pending": 0,
            "tickets_received_accepted": 0,
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"], expected)

    def test_saf_snapshot_complex(self):
        response = self.client.get(
            reverse("saf-operator-snapshot"),
            {"entity_id": self.entity.id, "year": 2022},
        )

        expected = {
            "ticket_sources_available": 10,
            "ticket_sources_history": 20,
            "tickets_assigned": 30,
            "tickets_assigned_pending": 15,
            "tickets_assigned_rejected": 5,
            "tickets_assigned_accepted": 10,
            "tickets_received": 0,
            "tickets_received_pending": 0,
            "tickets_received_accepted": 0,
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"], expected)

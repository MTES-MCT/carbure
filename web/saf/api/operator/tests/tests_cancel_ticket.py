from django.test import TestCase
from django.urls import reverse

from core.models import Entity
from core.tests_utils import setup_current_user
from saf.factories import SafTicketFactory, SafTicketSourceFactory
from saf.models import SafTicket, SafTicketSource


class SafCancelTicketTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/productionsites.json",
    ]

    def setUp(self):
        self.entity = Entity.objects.filter(entity_type=Entity.OPERATOR)[0]
        self.ticket_client = Entity.objects.filter(entity_type=Entity.OPERATOR)[1]
        self.user = setup_current_user(
            self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, "ADMIN")]
        )

        SafTicket.objects.all().delete()
        self.ticket_source = SafTicketSourceFactory.create(added_by_id=self.entity.id, total_volume=30000, assigned_volume=10000)  # fmt:skip

        SafTicket.objects.all().delete()
        self.ticket = SafTicketFactory.create(
            supplier_id=self.entity.id,
            client_id=self.ticket_client.id,
            volume=10000,
            parent_ticket_source_id=self.ticket_source.id,
        )

    def test_cancel_saf_ticket(self):
        query = {
            "entity_id": self.entity.id,
            "ticket_id": self.ticket.id,
        }

        response = self.client.post(reverse("saf-operator-cancel-ticket"), query)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")

        self.assertEqual(SafTicket.objects.count(), 0)

        ticket_source = SafTicketSource.objects.get(id=self.ticket_source.id)
        self.assertEqual(ticket_source.assigned_volume, 0)

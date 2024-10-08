from django.test import TestCase
from django.urls import reverse

from core.models import Entity
from core.tests_utils import setup_current_user
from saf.factories import SafTicketFactory
from saf.models import SafTicket


class SafTicketRejectTest(TestCase):
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
        self.supplier = Entity.objects.filter(entity_type=Entity.OPERATOR)[1]
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, "ADMIN")])

        SafTicket.objects.all().delete()
        self.ticket = SafTicketFactory.create(
            client_id=self.entity.id,
            supplier_id=self.supplier.id,
        )

    def test_reject_saf_ticket(self):
        query = {
            "entity_id": self.entity.id,
            "ticket_id": self.ticket.id,
        }

        response = self.client.post(reverse("saf-airline-reject-ticket"), query)

        assert response.status_code == 200
        assert response.json()["status"] == "success"

        assert SafTicket.objects.get(id=self.ticket.id).status == SafTicket.REJECTED

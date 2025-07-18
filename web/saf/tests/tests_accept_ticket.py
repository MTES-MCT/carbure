from django.urls import reverse

from saf.factories import SafTicketFactory
from saf.models import SafTicket
from saf.tests import TestCase


class SafCreditTicketSourceTest(TestCase):
    def setUp(self):
        super().setUp()

        self.ticket = SafTicketFactory.create(
            supplier_id=self.entity.id,
            client_id=self.airline.id,
            volume=10000,
            parent_ticket_source_id=self.ticket_source.id,
        )

    def test_accept_saf_ticket(self):
        self.ticket.status = SafTicket.PENDING
        self.ticket.save()
        query = {
            "entity_id": self.airline.id,
            "ticket_id": self.ticket.id,
            "ets_status": "ETS_VALUATION",
        }
        query_params = f"?entity_id={self.airline.id}"
        assert self.ticket.status == SafTicket.PENDING
        assert self.ticket.ets_status is None
        response = self.client.post(
            reverse("saf-tickets-accept", kwargs={"id": self.ticket.id}) + query_params,
            query,
        )

        assert response.status_code == 200
        self.ticket.refresh_from_db()
        assert self.ticket.status == SafTicket.ACCEPTED
        assert self.ticket.ets_status == "ETS_VALUATION"

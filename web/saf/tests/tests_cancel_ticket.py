from django.urls import reverse

from core.models import Entity
from saf.factories import SafTicketFactory, SafTicketSourceFactory
from saf.models import SafTicket, SafTicketSource
from saf.tests import TestCase


class SafCancelTicketTest(TestCase):
    def test_cancel_saf_ticket_ok(self):
        self.ticket.save()
        query = {
            "entity_id": self.entity.id,
            "ticket_id": self.ticket.id,
        }

        query_params = f"?entity_id={self.entity.id}"
        response = self.client.post(
            reverse("saf-tickets-cancel", kwargs={"id": self.ticket.id}) + query_params,
            query,
        )

        assert response.status_code == 200
        assert SafTicket.objects.count() == 0

        ticket_source = SafTicketSource.objects.get(id=self.ticket_source.id)
        assert ticket_source.assigned_volume == 0

    def test_cancel_saf_ticket_nok(self):
        self.entity = Entity.objects.create(entity_type=Entity.AIRLINE, name="Airline test")
        SafTicketSource.objects.all().delete()
        SafTicket.objects.all().delete()
        self.ticket_source = SafTicketSourceFactory.create(
            added_by_id=self.entity.id,
            delivery_period=202202,
            total_volume=30000,
            assigned_volume=10000,
        )

        self.ticket = SafTicketFactory.create(
            supplier_id=self.entity.id,
            client_id=self.ticket_client.id,
            volume=10000,
            parent_ticket_source_id=self.ticket_source.id,
        )
        self.ticket.save()
        query = {
            "entity_id": self.entity.id,
            "ticket_id": self.ticket.id,
        }

        query_params = f"?entity_id={self.entity.id}"
        response = self.client.post(
            reverse("saf-tickets-cancel", kwargs={"id": self.ticket.id}) + query_params,
            query,
        )

        assert response.status_code == 403
        assert SafTicket.objects.count() != 0

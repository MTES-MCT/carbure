from django.urls import reverse

from core.models import CarbureNotification, Entity, Pays
from core.tests_utils import setup_current_user
from saf.factories.saf_ticket_source import SafTicketSourceFactory
from saf.models import SafTicket
from saf.tests import TestCase


class SafExportForeignTicketTest(TestCase):
    def setUp(self):
        super().setUp()
        SafTicket.objects.all().delete()
        CarbureNotification.objects.all().delete()

    def export_ticket(self, body, ticket_source_id=None, entity_id=None):
        kwargs = {"id": ticket_source_id or self.ticket_source.id}
        return self.client.post(
            reverse("saf-ticket-sources-export-foreign", kwargs=kwargs),
            body,
            query_params={"entity_id": entity_id or self.entity.id},
        )

    def test_export_foreign_saf_ticket(self):
        export_country = Pays.objects.get(code_pays="ES")
        body = {
            "volume": 10000,
            "assignment_period": 202203,
            "export_country": export_country.code_pays,
            "unknown_airline_client": "Foreign Airline",
        }

        response = self.export_ticket(body)
        assert response.status_code == 200

        tickets = SafTicket.objects.all()
        assert tickets.count() == 1

        ticket = tickets[0]
        assert ticket.supplier_id == self.ticket_source.added_by_id
        assert ticket.client_id is None
        assert ticket.status == SafTicket.EXPORTED
        assert ticket.volume == 10000
        assert ticket.year == 2022
        assert ticket.assignment_period == 202203
        assert ticket.export_country_id == export_country.id
        assert ticket.unknown_airline_client == "Foreign Airline"
        assert ticket.parent_ticket_source_id == self.ticket_source.id

        self.ticket_source.refresh_from_db()
        assert self.ticket_source.assigned_volume == 20000
        assert CarbureNotification.objects.count() == 0

    def test_export_foreign_saf_ticket_fail_if_too_big(self):
        body = {
            "volume": 100000,
            "assignment_period": 202203,
            "export_country": "ES",
            "unknown_airline_client": "Foreign Airline",
        }

        response = self.export_ticket(body)

        assert response.status_code == 400
        assert response.json()["message"] == "VOLUME_TOO_BIG"
        assert SafTicket.objects.count() == 0

    def test_export_foreign_saf_ticket_fail_if_too_early(self):
        body = {
            "volume": 1000,
            "assignment_period": 202201,
            "export_country": "ES",
            "unknown_airline_client": "Foreign Airline",
        }

        response = self.export_ticket(body)

        assert response.status_code == 400
        assert response.json()["message"] == "ASSIGNMENT_BEFORE_DELIVERY"
        assert SafTicket.objects.count() == 0

    def test_export_foreign_saf_ticket_requires_export_fields(self):
        body = {
            "volume": 1000,
            "assignment_period": 202203,
            "export_country": "",
            "unknown_airline_client": "",
        }

        response = self.export_ticket(body)

        assert response.status_code == 400
        assert "export_country" in response.json()
        assert "unknown_airline_client" in response.json()
        assert SafTicket.objects.count() == 0

    def test_export_foreign_saf_ticket_allows_saf_trader_owner(self):
        saf_trader = Entity.objects.create(name="SAF Trader", entity_type=Entity.SAF_TRADER)
        ticket_source = SafTicketSourceFactory.create(
            added_by_id=saf_trader.id,
            delivery_period=202202,
            total_volume=30000,
            assigned_volume=10000,
        )
        self.client.logout()
        setup_current_user(
            self,
            "saf-trader@carbure.local",
            "SAF Trader",
            "gogogo",
            [(saf_trader, "ADMIN")],
        )

        body = {
            "volume": 1000,
            "assignment_period": 202203,
            "export_country": "ES",
            "unknown_airline_client": "Foreign Airline",
        }

        response = self.export_ticket(body, ticket_source_id=ticket_source.id, entity_id=saf_trader.id)

        assert response.status_code == 200, response.status_code

        ticket = SafTicket.objects.get()
        assert ticket.supplier_id == saf_trader.id
        assert ticket.status == SafTicket.EXPORTED
        assert ticket.volume == 1000

        ticket_source.refresh_from_db()
        assert ticket_source.assigned_volume == 11000

from django.urls import reverse

from saf.factories import SafTicketSourceFactory
from saf.models import SafTicket
from saf.tests import TestCase


class SafGroupedAssignTicketTest(TestCase):
    def setUp(self):
        super().setUp()

        self.ticket_source1 = SafTicketSourceFactory.create(
            added_by_id=self.entity.id, delivery_period=202202, total_volume=30000, assigned_volume=0
        )
        self.ticket_source2 = SafTicketSourceFactory.create(
            added_by_id=self.entity.id, delivery_period=202203, total_volume=20000, assigned_volume=0
        )
        self.ticket_source3 = SafTicketSourceFactory.create(
            added_by_id=self.entity.id, delivery_period=202204, total_volume=10000, assigned_volume=5000
        )

        SafTicket.objects.all().delete()

    def test_grouped_assign_saf_ticket_not_enough_volume(self):
        query = {
            "entity_id": self.entity.id,
            "ticket_sources_ids": [self.ticket_source1.id, self.ticket_source2.id],
            "client_id": self.ticket_client.id,
            "volume": 55000,
            "agreement_reference": "AGREF",
            "agreement_date": "2022-06-01",
            "assignment_period": 202204,
        }
        query_params = f"?entity_id={self.entity.id}"
        response = self.client.post(reverse("saf-ticket-sources-grouped-assign") + query_params, query)

        assert response.status_code == 400
        assert response.json()["message"] == "VOLUME_TOO_BIG"

    def test_grouped_assign_saf_ticket_too_early(self):
        query = {
            "entity_id": self.entity.id,
            "ticket_sources_ids": [self.ticket_source1.id, self.ticket_source2.id],
            "client_id": self.ticket_client.id,
            "volume": 40000,
            "agreement_reference": "AGREF",
            "agreement_date": "2022-06-01",
            "assignment_period": 202202,
        }

        query_params = f"?entity_id={self.entity.id}"
        response = self.client.post(reverse("saf-ticket-sources-grouped-assign") + query_params, query)

        assert response.status_code == 400
        assert response.json()["message"] == "ASSIGNMENT_BEFORE_DELIVERY"

    def test_grouped_assign_saf_ticket_ok(self):
        query = {
            "entity_id": self.entity.id,
            "ticket_sources_ids": [
                self.ticket_source1.id,
                self.ticket_source2.id,
                self.ticket_source3.id,
            ],
            "client_id": self.ticket_client.id,
            "volume": 55000,
            "agreement_reference": "AGREF",
            "agreement_date": "2022-06-01",
            "assignment_period": 202206,
        }

        query_params = f"?entity_id={self.entity.id}"
        response = self.client.post(reverse("saf-ticket-sources-grouped-assign") + query_params, query)

        assert response.status_code == 200
        assert response.json()["assigned_tickets_count"] == 3

        tickets = SafTicket.objects.all().order_by("created_at")
        assert tickets.count() == 3

        ticket = tickets[0]
        assert ticket.supplier_id == ticket.parent_ticket_source.added_by_id
        assert ticket.agreement_date.isoformat() == "2022-06-01"
        assert ticket.agreement_reference == "AGREF"
        assert ticket.status == "PENDING"
        assert ticket.carbure_id == "T%d-%s-%d" % (
            ticket.assignment_period,
            ticket.parent_ticket_source.production_country.code_pays,
            ticket.id,
        )
        assert ticket.client_id == self.ticket_client.id
        assert ticket.volume == 30000
        assert ticket.year == 2022
        assert ticket.assignment_period == 202206
        assert ticket.feedstock_id == ticket.parent_ticket_source.feedstock_id
        assert ticket.biofuel_id == ticket.parent_ticket_source.biofuel_id
        assert ticket.country_of_origin_id == ticket.parent_ticket_source.country_of_origin_id
        assert ticket.carbure_producer_id == ticket.parent_ticket_source.carbure_producer_id
        assert ticket.unknown_producer == ticket.parent_ticket_source.unknown_producer
        assert ticket.carbure_production_site_id == ticket.parent_ticket_source.carbure_production_site_id
        assert ticket.unknown_production_site == ticket.parent_ticket_source.unknown_production_site
        assert ticket.production_country_id == ticket.parent_ticket_source.production_country_id
        assert ticket.production_site_commissioning_date == ticket.parent_ticket_source.production_site_commissioning_date
        assert ticket.eec == ticket.parent_ticket_source.eec
        assert ticket.el == ticket.parent_ticket_source.el
        assert ticket.ep == ticket.parent_ticket_source.ep
        assert ticket.etd == ticket.parent_ticket_source.etd
        assert ticket.eu == ticket.parent_ticket_source.eu
        assert ticket.esca == ticket.parent_ticket_source.esca
        assert ticket.eccs == ticket.parent_ticket_source.eccs
        assert ticket.eccr == ticket.parent_ticket_source.eccr
        assert ticket.eee == ticket.parent_ticket_source.eee
        assert ticket.ghg_total == ticket.parent_ticket_source.ghg_total
        assert ticket.ghg_reference == ticket.parent_ticket_source.ghg_reference
        assert ticket.ghg_reduction == ticket.parent_ticket_source.ghg_reduction
        assert ticket.parent_ticket_source_id == ticket.parent_ticket_source.id
        assert ticket.parent_ticket_source.assigned_volume == 30000

        assert tickets[1].volume == 20000
        assert tickets[1].parent_ticket_source.assigned_volume == 20000
        assert tickets[2].volume == 5000
        assert tickets[2].parent_ticket_source.assigned_volume == 10000

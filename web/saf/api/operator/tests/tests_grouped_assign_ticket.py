from datetime import datetime
from django.test import TestCase
from django.urls import reverse


from core.tests_utils import setup_current_user
from core.models import Entity
from saf.factories import SafTicketSourceFactory
from saf.models import SafTicketSource, SafTicket


class SafGroupedAssignTicketTest(TestCase):
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

        SafTicketSource.objects.all().delete()
        self.ticket_source1 = SafTicketSourceFactory.create(added_by_id=self.entity.id, delivery_period=202202, total_volume=30000, assigned_volume=0)  # fmt:skip
        self.ticket_source2 = SafTicketSourceFactory.create(added_by_id=self.entity.id, delivery_period=202203, total_volume=20000, assigned_volume=0)  # fmt:skip
        self.ticket_source3 = SafTicketSourceFactory.create(added_by_id=self.entity.id, delivery_period=202204, total_volume=10000, assigned_volume=5000)  # fmt:skip

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

        response = self.client.post(
            reverse("saf-operator-grouped-assign-ticket"), query
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["status"], "error")
        self.assertEqual(response.json()["error"], "VOLUME_TOO_BIG")

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

        response = self.client.post(
            reverse("saf-operator-grouped-assign-ticket"), query
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["status"], "error")
        self.assertEqual(response.json()["error"], "ASSIGNMENT_BEFORE_DELIVERY")

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

        response = self.client.post(
            reverse("saf-operator-grouped-assign-ticket"), query
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        self.assertEqual(response.json()["data"]["assigned_tickets_count"], 3)

        tickets = SafTicket.objects.all().order_by("created_at")
        self.assertEqual(tickets.count(), 3)

        ticket = tickets[0]
        self.assertEqual(ticket.supplier_id, ticket.parent_ticket_source.added_by_id)
        self.assertEqual(ticket.agreement_date.isoformat(), "2022-06-01")
        self.assertEqual(ticket.agreement_reference, "AGREF")
        self.assertEqual(ticket.status, "PENDING")
        self.assertEqual(ticket.carbure_id, "T%d-%s-%d" % (ticket.assignment_period, ticket.parent_ticket_source.production_country.code_pays, ticket.id))  # fmt:skip
        self.assertEqual(ticket.client_id, self.ticket_client.id)
        self.assertEqual(ticket.volume, 30000)
        self.assertEqual(ticket.year, 2022)
        self.assertEqual(ticket.assignment_period, 202206)
        self.assertEqual(ticket.feedstock_id, ticket.parent_ticket_source.feedstock_id)
        self.assertEqual(ticket.biofuel_id, ticket.parent_ticket_source.biofuel_id)
        self.assertEqual(
            ticket.country_of_origin_id,
            ticket.parent_ticket_source.country_of_origin_id,
        )
        self.assertEqual(
            ticket.carbure_producer_id, ticket.parent_ticket_source.carbure_producer_id
        )
        self.assertEqual(
            ticket.unknown_producer, ticket.parent_ticket_source.unknown_producer
        )
        self.assertEqual(
            ticket.carbure_production_site_id,
            ticket.parent_ticket_source.carbure_production_site_id,
        )
        self.assertEqual(
            ticket.unknown_production_site,
            ticket.parent_ticket_source.unknown_production_site,
        )
        self.assertEqual(
            ticket.production_country_id,
            ticket.parent_ticket_source.production_country_id,
        )
        self.assertEqual(ticket.production_site_commissioning_date, ticket.parent_ticket_source.production_site_commissioning_date)  # fmt:skip
        self.assertEqual(ticket.eec, ticket.parent_ticket_source.eec)
        self.assertEqual(ticket.el, ticket.parent_ticket_source.el)
        self.assertEqual(ticket.ep, ticket.parent_ticket_source.ep)
        self.assertEqual(ticket.etd, ticket.parent_ticket_source.etd)
        self.assertEqual(ticket.eu, ticket.parent_ticket_source.eu)
        self.assertEqual(ticket.esca, ticket.parent_ticket_source.esca)
        self.assertEqual(ticket.eccs, ticket.parent_ticket_source.eccs)
        self.assertEqual(ticket.eccr, ticket.parent_ticket_source.eccr)
        self.assertEqual(ticket.eee, ticket.parent_ticket_source.eee)
        self.assertEqual(ticket.ghg_total, ticket.parent_ticket_source.ghg_total)
        self.assertEqual(
            ticket.ghg_reference, ticket.parent_ticket_source.ghg_reference
        )
        self.assertEqual(
            ticket.ghg_reduction, ticket.parent_ticket_source.ghg_reduction
        )
        self.assertEqual(ticket.parent_ticket_source_id, ticket.parent_ticket_source.id)
        self.assertEqual(ticket.parent_ticket_source.assigned_volume, 30000)

        self.assertEqual(tickets[1].volume, 20000)
        self.assertEqual(tickets[1].parent_ticket_source.assigned_volume, 20000)
        self.assertEqual(tickets[2].volume, 5000)
        self.assertEqual(tickets[2].parent_ticket_source.assigned_volume, 10000)

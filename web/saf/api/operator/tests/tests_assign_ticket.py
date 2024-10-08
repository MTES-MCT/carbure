from datetime import datetime

from django.test import TestCase
from django.urls import reverse

from core.models import Entity
from core.tests_utils import setup_current_user
from saf.factories import SafTicketSourceFactory
from saf.models import SafTicket, SafTicketSource


class SafAssignTicketTest(TestCase):
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
        self.ticket_client = Entity.objects.filter(entity_type=Entity.OPERATOR)[1]
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, "ADMIN")])

        SafTicketSource.objects.all().delete()
        self.ticket_source = SafTicketSourceFactory.create(
            added_by_id=self.entity.id, delivery_period=202202, total_volume=30000, assigned_volume=0
        )

        SafTicket.objects.all().delete()

    def test_assign_saf_ticket(self):
        query = {
            "entity_id": self.entity.id,
            "ticket_source_id": self.ticket_source.id,
            "client_id": self.ticket_client.id,
            "volume": 10000,
            "agreement_reference": "AGREF",
            "agreement_date": "2022-06-01",
            "assignment_period": 202203,
        }

        datetime.today()

        response = self.client.post(reverse("saf-operator-assign-ticket"), query)

        assert response.status_code == 200
        assert response.json()["status"] == "success"

        tickets = SafTicket.objects.all()
        assert tickets.count() == 1

        ticket = tickets[0]
        assert ticket.supplier_id == self.ticket_source.added_by_id
        assert ticket.agreement_date.isoformat() == "2022-06-01"
        assert ticket.agreement_reference == "AGREF"
        assert ticket.status == "PENDING"
        assert ticket.carbure_id == "T%d-%s-%d" % (
            ticket.assignment_period,
            self.ticket_source.production_country.code_pays,
            ticket.id,
        )
        assert ticket.client_id == self.ticket_client.id
        assert ticket.volume == 10000
        assert ticket.year == 2022
        assert ticket.assignment_period == 202203
        assert ticket.feedstock_id == self.ticket_source.feedstock_id
        assert ticket.biofuel_id == self.ticket_source.biofuel_id
        assert ticket.country_of_origin_id == self.ticket_source.country_of_origin_id
        assert ticket.carbure_producer_id == self.ticket_source.carbure_producer_id
        assert ticket.unknown_producer == self.ticket_source.unknown_producer
        assert ticket.carbure_production_site_id == self.ticket_source.carbure_production_site_id
        assert ticket.unknown_production_site == self.ticket_source.unknown_production_site
        assert ticket.production_country_id == self.ticket_source.production_country_id
        assert ticket.production_site_commissioning_date == self.ticket_source.production_site_commissioning_date
        assert ticket.eec == self.ticket_source.eec
        assert ticket.el == self.ticket_source.el
        assert ticket.ep == self.ticket_source.ep
        assert ticket.etd == self.ticket_source.etd
        assert ticket.eu == self.ticket_source.eu
        assert ticket.esca == self.ticket_source.esca
        assert ticket.eccs == self.ticket_source.eccs
        assert ticket.eccr == self.ticket_source.eccr
        assert ticket.eee == self.ticket_source.eee
        assert ticket.ghg_total == self.ticket_source.ghg_total
        assert ticket.ghg_reference == self.ticket_source.ghg_reference
        assert ticket.ghg_reduction == self.ticket_source.ghg_reduction
        assert ticket.parent_ticket_source_id == self.ticket_source.id

    def test_assign_saf_ticket_fail_if_too_big(self):
        query = {
            "entity_id": self.entity.id,
            "ticket_source_id": self.ticket_source.id,
            "client_id": self.ticket_client.id,
            "volume": 100000,
            "agreement_reference": "AGREF",
            "agreement_date": "2022-06-01",
            "assignment_period": 202203,
        }

        response = self.client.post(reverse("saf-operator-assign-ticket"), query)

        assert response.status_code == 400
        assert response.json()["error"] == "VOLUME_TOO_BIG"

    def test_assign_saf_ticket_fail_if_too_early(self):
        query = {
            "entity_id": self.entity.id,
            "ticket_source_id": self.ticket_source.id,
            "client_id": self.ticket_client.id,
            "volume": 1000,
            "agreement_reference": "AGREF",
            "agreement_date": "2022-06-01",
            "assignment_period": 202201,
        }

        response = self.client.post(reverse("saf-operator-assign-ticket"), query)

        assert response.status_code == 400
        assert response.json()["error"] == "ASSIGNMENT_BEFORE_DELIVERY"

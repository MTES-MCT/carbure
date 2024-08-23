from django.test import TestCase
from django.urls import reverse

from core.models import Entity, MatierePremiere
from core.tests_utils import setup_current_user
from saf.factories import SafTicketFactory
from saf.models import SafTicket


class SafTicketFiltersTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/productionsites.json",
    ]

    def setUp(self):
        self.entity = Entity.objects.filter(entity_type=Entity.OPERATOR)[0]
        self.supplier1 = Entity.objects.filter(entity_type=Entity.OPERATOR)[1]
        self.supplier2 = Entity.objects.filter(entity_type=Entity.OPERATOR)[2]
        self.user = setup_current_user(
            self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, "ADMIN")]
        )

        self.hau = MatierePremiere.objects.get(code="HUILE_ALIMENTAIRE_USAGEE")
        self.hga = MatierePremiere.objects.get(
            code="HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2"
        )

        SafTicket.objects.all().delete()

        SafTicketFactory.create(year=2022, assignment_period=202201, client_id=self.entity.id, supplier_id=self.supplier1.id, feedstock=self.hau, status=SafTicket.PENDING)  # fmt:skip
        SafTicketFactory.create(year=2022, assignment_period=202202, client_id=self.entity.id, supplier_id=self.supplier1.id, feedstock=self.hau, status=SafTicket.ACCEPTED)  # fmt:skip
        SafTicketFactory.create(year=2022, assignment_period=202202, client_id=self.entity.id, supplier_id=self.supplier2.id, feedstock=self.hga, status=SafTicket.PENDING)  # fmt:skip

    def test_empty_ticket_filters(self):
        query = {
            "entity_id": self.entity.id,
            "year": 2021,
            "status": "PENDING",
            "filter": "feedstocks",
        }
        response = self.client.get(reverse("saf-airline-ticket-filters"), query)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"], [])

    def test_ticket_filters_feedstock(self):
        query = {
            "entity_id": self.entity.id,
            "year": 2022,
            "status": "PENDING",
            "filter": "feedstocks",
        }
        response = self.client.get(reverse("saf-airline-ticket-filters"), query)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            sorted(response.json()["data"]),
            sorted(
                ["HUILE_ALIMENTAIRE_USAGEE", "HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2"]
            ),
        )

    def test_ticket_filters_period_feedstock(self):
        query = {
            "entity_id": self.entity.id,
            "year": 2022,
            "status": "PENDING",
            "filter": "feedstocks",
            "periods": 202201,
        }
        response = self.client.get(reverse("saf-airline-ticket-filters"), query)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            sorted(response.json()["data"]),
            sorted(["HUILE_ALIMENTAIRE_USAGEE"]),
        )

    def test_ticket_filters_period(self):
        query = {
            "entity_id": self.entity.id,
            "year": 2022,
            "status": "PENDING",
            "filter": "periods",
        }
        response = self.client.get(reverse("saf-airline-ticket-filters"), query)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            sorted(response.json()["data"]),
            sorted([202201, 202202]),
        )

    def test_ticket_filters_supplier(self):
        query = {
            "entity_id": self.entity.id,
            "year": 2022,
            "status": "PENDING",
            "filter": "suppliers",
        }
        response = self.client.get(reverse("saf-airline-ticket-filters"), query)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            sorted(response.json()["data"]),
            sorted([self.supplier1.name, self.supplier2.name]),
        )

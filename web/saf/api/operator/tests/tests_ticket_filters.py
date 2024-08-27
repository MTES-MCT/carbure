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
        self.client1 = Entity.objects.filter(entity_type=Entity.OPERATOR)[1]
        self.client2 = Entity.objects.filter(entity_type=Entity.OPERATOR)[2]
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, "ADMIN")])

        self.hau = MatierePremiere.objects.get(code="HUILE_ALIMENTAIRE_USAGEE")
        self.hga = MatierePremiere.objects.get(code="HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2")

        SafTicket.objects.all().delete()

        SafTicketFactory.create(
            year=2022,
            assignment_period=202201,
            supplier_id=self.entity.id,
            client_id=self.client1.id,
            feedstock=self.hau,
            status=SafTicket.PENDING,
        )
        SafTicketFactory.create(
            year=2022,
            assignment_period=202202,
            supplier_id=self.entity.id,
            client_id=self.client2.id,
            feedstock=self.hau,
            status=SafTicket.ACCEPTED,
        )
        SafTicketFactory.create(
            year=2022,
            assignment_period=202202,
            supplier_id=self.entity.id,
            client_id=self.client2.id,
            feedstock=self.hga,
            status=SafTicket.PENDING,
        )

    def test_empty_ticket_filters(self):
        query = {
            "entity_id": self.entity.id,
            "year": 2021,
            "status": "PENDING",
            "type": "assigned",
            "filter": "feedstocks",
        }
        response = self.client.get(reverse("saf-operator-ticket-filters"), query)
        assert response.status_code == 200
        assert response.json()["data"] == []

    def test_ticket_filters_feedstock(self):
        query = {
            "entity_id": self.entity.id,
            "year": 2022,
            "status": "PENDING",
            "type": "assigned",
            "filter": "feedstocks",
        }
        response = self.client.get(reverse("saf-operator-ticket-filters"), query)

        assert response.status_code == 200
        assert sorted(response.json()["data"]) == sorted(
            ["HUILE_ALIMENTAIRE_USAGEE", "HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2"]
        )

    def test_ticket_filters_period_feedstock(self):
        query = {
            "entity_id": self.entity.id,
            "year": 2022,
            "status": "PENDING",
            "type": "assigned",
            "filter": "feedstocks",
            "periods": 202201,
        }
        response = self.client.get(reverse("saf-operator-ticket-filters"), query)

        assert response.status_code == 200
        assert sorted(response.json()["data"]) == sorted(["HUILE_ALIMENTAIRE_USAGEE"])

    def test_ticket_filters_period(self):
        query = {
            "entity_id": self.entity.id,
            "year": 2022,
            "status": "PENDING",
            "type": "assigned",
            "filter": "periods",
        }
        response = self.client.get(reverse("saf-operator-ticket-filters"), query)

        assert response.status_code == 200
        assert sorted(response.json()["data"]) == sorted([202201, 202202])

    def test_ticket_filters_client(self):
        query = {
            "entity_id": self.entity.id,
            "year": 2022,
            "status": "PENDING",
            "type": "assigned",
            "filter": "clients",
        }
        response = self.client.get(reverse("saf-operator-ticket-filters"), query)

        assert response.status_code == 200
        assert sorted(response.json()["data"]) == sorted([self.client1.name, self.client2.name])

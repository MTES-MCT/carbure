from django.urls import reverse

from core.models import MatierePremiere
from saf.factories import SafTicketFactory
from saf.models import SafTicket
from saf.tests import TestCase


class SafTicketFiltersTest(TestCase):
    def setUp(self):
        super().setUp()

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
        response = self.client.get(reverse("saf-tickets-filters"), query)
        assert response.status_code == 200
        assert response.json() == []

    def test_ticket_filters_feedstock(self):
        query = {
            "entity_id": self.entity.id,
            "year": 2022,
            "status": "PENDING",
            "type": "assigned",
            "filter": "feedstocks",
        }
        response = self.client.get(reverse("saf-tickets-filters"), query)

        assert response.status_code == 200
        assert sorted(response.json()) == sorted(["HUILE_ALIMENTAIRE_USAGEE", "HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2"])

    def test_ticket_filters_period_feedstock(self):
        query = {
            "entity_id": self.entity.id,
            "year": 2022,
            "status": "PENDING",
            "type": "assigned",
            "filter": "feedstocks",
            "periods": 202201,
        }
        response = self.client.get(reverse("saf-tickets-filters"), query)

        assert response.status_code == 200
        assert sorted(response.json()) == sorted(["HUILE_ALIMENTAIRE_USAGEE"])

    def test_ticket_filters_period(self):
        query = {
            "entity_id": self.entity.id,
            "year": 2022,
            "status": "PENDING",
            "type": "assigned",
            "filter": "periods",
        }
        response = self.client.get(reverse("saf-tickets-filters"), query)

        assert response.status_code == 200
        assert sorted(response.json()) == sorted([202201, 202202])

    def test_ticket_filters_client(self):
        query = {
            "entity_id": self.entity.id,
            "year": 2022,
            "status": "PENDING",
            "type": "assigned",
            "filter": "clients",
        }
        response = self.client.get(reverse("saf-tickets-filters"), query)

        assert response.status_code == 200
        assert sorted(response.json()) == sorted([self.client1.name, self.client2.name])

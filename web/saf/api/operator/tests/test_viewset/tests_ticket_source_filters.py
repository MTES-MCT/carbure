from django.urls import reverse

from core.models import MatierePremiere
from saf.api.operator.tests.test_viewset import TestCase
from saf.factories import SafTicketFactory, SafTicketSourceFactory
from saf.models import SafTicket, SafTicketSource


class SafTicketSourceFiltersTest(TestCase):
    def setUp(self):
        super().setUp()

        self.ble = MatierePremiere.objects.get(code="BLE")
        self.colza = MatierePremiere.objects.get(code="COLZA")
        self.hau = MatierePremiere.objects.get(code="HUILE_ALIMENTAIRE_USAGEE")
        self.hga = MatierePremiere.objects.get(code="HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2")

        SafTicketSource.objects.all().delete()
        SafTicket.objects.all().delete()
        self.ticket_sources = [
            SafTicketSourceFactory.create(
                year=2022,
                delivery_period=202201,
                added_by_id=self.entity.id,
                feedstock=self.hau,
            ),
            SafTicketSourceFactory.create(
                year=2022,
                delivery_period=202201,
                added_by_id=self.entity.id,
                feedstock=self.hga,
            ),
            SafTicketSourceFactory.create(
                year=2022,
                delivery_period=202201,
                added_by_id=self.entity.id,
                feedstock=self.ble,
            ),
            SafTicketSourceFactory.create(
                year=2022,
                delivery_period=202201,
                added_by_id=self.entity.id,
                feedstock=self.colza,
            ),
            SafTicketSourceFactory.create(
                year=2022,
                delivery_period=202202,
                added_by_id=self.entity.id,
                feedstock=self.hau,
            ),
            SafTicketSourceFactory.create(
                year=2022,
                delivery_period=202202,
                added_by_id=self.entity.id,
                feedstock=self.hga,
            ),
        ]

        first_id = self.ticket_sources[0].id

        SafTicket.objects.all().delete()
        SafTicketFactory.create(
            year=2022,
            supplier_id=self.entity.id,
            client_id=self.client1.id,
            status=SafTicket.PENDING,
            parent_ticket_source_id=first_id,
        )
        SafTicketFactory.create(
            year=2022,
            supplier_id=self.entity.id,
            client_id=self.client2.id,
            status=SafTicket.PENDING,
            parent_ticket_source_id=first_id,
        )

    def test_empty_ticket_source_filters(self):
        query = {
            "entity_id": self.entity.id,
            "year": 2021,
            "status": "AVAILABLE",
            "filter": "feedstocks",
        }
        response = self.client.get(reverse("saf-ticket-sources-filters"), query)
        assert response.status_code == 200
        assert response.json() == []

    def test_ticket_source_filters_feedstock(self):
        query = {
            "entity_id": self.entity.id,
            "year": 2022,
            "status": "AVAILABLE",
            "filter": "feedstocks",
        }
        response = self.client.get(reverse("saf-ticket-sources-filters"), query)

        assert response.status_code == 200
        assert sorted(response.json()) == sorted(
            ["HUILE_ALIMENTAIRE_USAGEE", "HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2", "BLE", "COLZA"]
        )

    def test_ticket_source_filters_period_feedstock(self):
        query = {
            "entity_id": self.entity.id,
            "year": 2022,
            "status": "AVAILABLE",
            "filter": "feedstocks",
            "periods": 202202,
        }
        response = self.client.get(reverse("saf-ticket-sources-filters"), query)

        assert response.status_code == 200
        assert sorted(response.json()) == sorted(["HUILE_ALIMENTAIRE_USAGEE", "HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2"])

    def test_ticket_source_filters_period(self):
        query = {
            "entity_id": self.entity.id,
            "year": 2022,
            "status": "AVAILABLE",
            "filter": "periods",
        }
        response = self.client.get(reverse("saf-ticket-sources-filters"), query)

        assert response.status_code == 200
        assert sorted(response.json()) == sorted([202201, 202202])

    def test_ticket_source_filters_client(self):
        query = {
            "entity_id": self.entity.id,
            "year": 2022,
            "status": "AVAILABLE",
            "filter": "clients",
        }
        response = self.client.get(reverse("saf-ticket-sources-filters"), query)

        assert response.status_code == 200
        assert sorted(response.json()) == sorted([self.client1.name, self.client2.name])

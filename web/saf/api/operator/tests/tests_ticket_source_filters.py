from django.test import TestCase
from django.urls import reverse


from core.tests_utils import setup_current_user
from core.models import Entity, MatierePremiere
from saf.factories import SafTicketSourceFactory, SafTicketFactory
from saf.models import SafTicketSource, SafTicket


class SafTicketSourceFiltersTest(TestCase):
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
        self.user = setup_current_user(
            self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, "ADMIN")]
        )

        self.ble = MatierePremiere.objects.get(code="BLE")
        self.colza = MatierePremiere.objects.get(code="COLZA")
        self.hau = MatierePremiere.objects.get(code="HUILE_ALIMENTAIRE_USAGEE")
        self.hga = MatierePremiere.objects.get(
            code="HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2"
        )

        SafTicketSource.objects.all().delete()

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
        SafTicketFactory.create(year=2022, supplier_id=self.entity.id, client_id=self.client1.id, status=SafTicket.PENDING, parent_ticket_source_id=first_id)  # fmt:skip
        SafTicketFactory.create(year=2022, supplier_id=self.entity.id, client_id=self.client2.id, status=SafTicket.PENDING, parent_ticket_source_id=first_id)  # fmt:skip

    def test_empty_ticket_source_filters(self):
        query = {
            "entity_id": self.entity.id,
            "year": 2021,
            "status": "AVAILABLE",
            "filter": "feedstocks",
        }
        response = self.client.get(reverse("saf-operator-ticket-source-filters"), query)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"], [])

    def test_ticket_source_filters_feedstock(self):
        query = {
            "entity_id": self.entity.id,
            "year": 2022,
            "status": "AVAILABLE",
            "filter": "feedstocks",
        }
        response = self.client.get(reverse("saf-operator-ticket-source-filters"), query)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            sorted(response.json()["data"]),
            sorted(
                [
                    "HUILE_ALIMENTAIRE_USAGEE",
                    "HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2",
                    "BLE",
                    "COLZA",
                ]
            ),
        )

    def test_ticket_source_filters_period_feedstock(self):
        query = {
            "entity_id": self.entity.id,
            "year": 2022,
            "status": "AVAILABLE",
            "filter": "feedstocks",
            "periods": 202202,
        }
        response = self.client.get(reverse("saf-operator-ticket-source-filters"), query)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            sorted(response.json()["data"]),
            sorted(
                ["HUILE_ALIMENTAIRE_USAGEE", "HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2"]
            ),
        )

    def test_ticket_source_filters_period(self):
        query = {
            "entity_id": self.entity.id,
            "year": 2022,
            "status": "AVAILABLE",
            "filter": "periods",
        }
        response = self.client.get(reverse("saf-operator-ticket-source-filters"), query)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            sorted(response.json()["data"]),
            sorted([202201, 202202]),
        )

    def test_ticket_source_filters_client(self):
        query = {
            "entity_id": self.entity.id,
            "year": 2022,
            "status": "AVAILABLE",
            "filter": "clients",
        }
        response = self.client.get(reverse("saf-operator-ticket-source-filters"), query)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            sorted(response.json()["data"]),
            sorted([self.client1.name, self.client2.name]),
        )

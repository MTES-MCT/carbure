from datetime import datetime

from django.urls import reverse

from core.models import Biocarburant, MatierePremiere, Pays
from saf.models import SafTicket, SafTicketSource
from saf.tests import TestCase


class SafTicketSourcesTest(TestCase):
    def setUp(self):
        super().setUp()
        SafTicketSource.objects.all().delete()
        SafTicket.objects.all().delete()

        self.ticket_source = SafTicketSource.objects.create(
            id=1234,
            carbure_id="carbure-id-001",
            added_by=self.entity,
            created_at=datetime(2022, 1, 1),
            year=2022,
            delivery_period=202201,
            total_volume=30000,
            assigned_volume=0,
            feedstock=MatierePremiere.objects.get(code="HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2"),
            biofuel=Biocarburant.objects.get(code="HCC"),
            country_of_origin=Pays.objects.get(name="Espagne"),
            carbure_producer=None,
            unknown_producer="External Producer",
            carbure_production_site=None,
            unknown_production_site="External Production Site",
            production_country=Pays.objects.get(name="Espagne"),
            production_site_commissioning_date="2001-01-01",
            eec=1,
            el=1,
            ep=1,
            etd=1,
            eu=1,
            esca=1,
            eccs=1,
            eccr=1,
            eee=1,
            ghg_total=1,
            ghg_reference=60,
            ghg_reduction=65,
            parent_lot=None,
        )

        # create a second ticket to check pagination
        self.second_ticket_source = self.ticket_source
        self.second_ticket_source.pk = 12345
        self.second_ticket_source.carbure_id = "carbure-id-002"
        self.second_ticket_source.save()

        self.ticket = SafTicket.objects.create(
            id=4321,
            carbure_id="carbure-id-t-001",
            created_at=datetime(2022, 1, 1),
            year=2022,
            assignment_period=202201,
            status=SafTicket.PENDING,
            volume=30000,
            feedstock=MatierePremiere.objects.get(code="HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2"),
            biofuel=Biocarburant.objects.get(code="HCC"),
            country_of_origin=Pays.objects.get(name="Espagne"),
            supplier=self.entity,
            client=self.ticket_client,
            agreement_date="2022-06-20",
            carbure_producer=None,
            unknown_producer="External Producer",
            carbure_production_site=None,
            unknown_production_site="External Production Site",
            production_country=Pays.objects.get(name="Espagne"),
            production_site_commissioning_date="2001-01-01",
            eec=1,
            el=1,
            ep=1,
            etd=1,
            eu=1,
            esca=1,
            eccs=1,
            eccr=1,
            eee=1,
            ghg_total=1,
            ghg_reference=60,
            ghg_reduction=65,
            parent_ticket_source_id=1234,
        )

    def test_saf_ticket_sources(self):
        query = {
            "entity_id": self.entity.id,
            "year": 2022,
            "status": "AVAILABLE",
            "from_idx": 0,
            "limit": 1,
        }
        # response = self.client.get(reverse("saf-operator-ticket-sources"), query)
        response = self.client.get(reverse("saf-ticket-sources-list"), query)
        assert response.status_code == 200

        expected_ticket_source = {
            "id": 1234,
            "carbure_id": "carbure-id-001",
            "year": 2022,
            "delivery_period": 202201,
            "total_volume": 30000.0,
            "assigned_volume": 0.0,
            "feedstock": {
                "name": "Huiles ou graisses animales  (catégorie I et/ou II )",
                "name_en": "CI/CII Animal fat",
                "code": "HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2",
                "category": "ANN-IX-B",
                "is_double_compte": True,
            },
            "biofuel": {
                "name": "Huile cotraitée - Carburéacteur",
                "name_en": "Co-processed oil - jet",
                "code": "HCC",
            },
            "country_of_origin": {
                "name": "Espagne",
                "name_en": "Spain",
                "code_pays": "ES",
                "is_in_europe": True,
            },
            "ghg_reduction": 65.0,
            "parent_lot": None,
            "assigned_tickets": [
                {
                    "agreement_date": "2022-06-20",
                    "assignment_period": 202201,
                    "carbure_id": "carbure-id-t-001",
                    "client": self.ticket_client.name,
                    "id": 4321,
                    "status": "PENDING",
                    "volume": 30000.0,
                }
            ],
            "parent_ticket": None,
            "added_by": {
                "id": 14,
                "name": "AOT",
                "entity_type": "Opérateur",
            },
        }

        # do not check created_at as its automatically generated
        response_ticket_source = response.json()["results"][0]
        response_ticket_source.pop("created_at")
        response_ticket_source["assigned_tickets"][0].pop("created_at")

        assert response_ticket_source == expected_ticket_source
        assert response.json()["count"] == 2

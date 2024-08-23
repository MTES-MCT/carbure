from datetime import datetime

from django.test import TestCase
from django.urls import reverse

from core.models import Biocarburant, Entity, MatierePremiere, Pays
from core.tests_utils import setup_current_user
from saf.models import SafTicket, SafTicketSource


class SafTicketSourceDetailsTest(TestCase):
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
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, "ADMIN")])

        SafTicketSource.objects.all().delete()
        SafTicket.objects.all().delete()

        self.ticket_source = SafTicketSource.objects.create(
            id=1234,
            carbure_id="carbure-id-001",
            added_by=self.entity,
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

        # force creation date to overwrite autodate
        self.ticket_source.created_at = "2022-01-01T00:00:00.000000+00:00"
        self.ticket_source.save()

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
        query = {"entity_id": self.entity.id, "ticket_source_id": 1234}
        response = self.client.get(reverse("saf-operator-ticket-source-details"), query)

        assert response.status_code == 200

        expected_ticket_source = {
            "id": 1234,
            "carbure_id": "carbure-id-001",
            "year": 2022,
            "delivery_period": 202201,
            "total_volume": 30000.0,
            "assigned_volume": 0.0,
            "carbure_producer": None,
            "unknown_producer": "External Producer",
            "carbure_production_site": None,
            "unknown_production_site": "External Production Site",
            "production_site_commissioning_date": "2001-01-01",
            "added_by": {
                "id": self.entity.id,
                "name": self.entity.name,
                "entity_type": self.entity.entity_type,
            },
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
            "eccr": 1.0,
            "eccs": 1.0,
            "eec": 1.0,
            "eee": 1.0,
            "el": 1.0,
            "ep": 1.0,
            "esca": 1.0,
            "etd": 1.0,
            "eu": 1.0,
            "ghg_total": 1.0,
            "ghg_reduction": 65.0,
            "assigned_tickets": [
                {
                    "agreement_date": "2022-06-20",
                    "carbure_id": "carbure-id-t-001",
                    "client": self.ticket_client.name,
                    "id": 4321,
                    "status": "PENDING",
                    "volume": 30000.0,
                }
            ],
            "parent_lot": None,
        }

        # do not check created_at as its automatically generated
        response_ticket_source = response.json()["data"]
        response_ticket_source.pop("created_at")
        response_ticket_source["assigned_tickets"][0].pop("created_at")

        assert response.json()["data"] == expected_ticket_source

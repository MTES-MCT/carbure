from datetime import datetime

from django.test import TestCase
from django.urls import reverse

from core.models import Biocarburant, Entity, MatierePremiere, Pays
from core.tests_utils import setup_current_user
from saf.models import SafTicket, SafTicketSource


class SafTicketDetailsTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/productionsites.json",
    ]

    def setUp(self):
        self.entity = Entity.objects.filter(entity_type=Entity.OPERATOR)[0]
        self.supplier = Entity.objects.filter(entity_type=Entity.OPERATOR)[1]
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, "ADMIN")])

        SafTicketSource.objects.all().delete()
        SafTicket.objects.all().delete()

        self.ticket_source = SafTicketSource.objects.create(
            id=1234,
            carbure_id="carbure-id-001",
            added_by=self.supplier,
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
            supplier=self.supplier,
            client=self.entity,
            free_field="Everything looks fine",
            agreement_date="2022-06-20",
            agreement_reference="ABCD",
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

        # force creation date to overwrite autodate
        self.ticket.created_at = "2022-01-01T00:00:00.000000+00:00"
        self.ticket.save()

    def test_saf_ticket_sources(self):
        query = {"entity_id": self.entity.id, "ticket_id": 4321}
        response = self.client.get(reverse("saf-airline-ticket-details"), query)

        assert response.status_code == 200

        expected_ticket = {
            "id": 4321,
            "carbure_id": "carbure-id-t-001",
            "year": 2022,
            "assignment_period": 202201,
            "created_at": "2022-01-01T01:00:00+01:00",
            "status": "PENDING",
            "volume": 30000.0,
            "agreement_date": "2022-06-20",
            "agreement_reference": "ABCD",
            "carbure_producer": None,
            "unknown_producer": "External Producer",
            "carbure_production_site": None,
            "unknown_production_site": "External Production Site",
            "production_site_commissioning_date": "2001-01-01",
            "supplier": self.supplier.name,
            "client": self.entity.name,
            "free_field": "Everything looks fine",
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
            "client_comment": None,
            "parent_ticket_source": {
                "id": 1234,
                "carbure_id": "carbure-id-001",
                "total_volume": 30000.0,
                "assigned_volume": 0.0,
            },
        }

        assert response.json()["data"] == expected_ticket

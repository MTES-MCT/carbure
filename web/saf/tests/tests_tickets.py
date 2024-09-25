from datetime import datetime

from django.urls import reverse

from core.models import Biocarburant, MatierePremiere, Pays
from saf.api.operator.tests.test_viewset import TestCase
from saf.models import SafTicket, SafTicketSource


class SafTicketsTest(TestCase):
    def setUp(self):
        super().setUp()

        SafTicketSource.objects.all().delete()
        SafTicket.objects.all().delete()

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
            agreement_reference="ABCD",
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
            parent_ticket_source_id=None,
        )

        self.second_ticket = self.ticket
        self.second_ticket.pk = 54321
        self.second_ticket.carbure_id = "carbure-id-t-002"
        self.second_ticket.save()

    def test_saf_tickets(self):
        query = {
            "entity_id": self.entity.id,
            "year": 2022,
            "from_idx": 0,
            "limit": 1,
            "status": "PENDING",
            "type": "assigned",
        }

        # response = self.client.get(reverse("saf-operator-tickets"), query)
        response = self.client.get(reverse("saf-tickets-list"), query)
        assert response.status_code == 200

        expected_ticket = {
            "id": 4321,
            "carbure_id": "carbure-id-t-001",
            "year": 2022,
            "assignment_period": 202201,
            "status": "PENDING",
            "supplier": self.entity.name,
            "client": self.ticket_client.name,
            "volume": 30000.0,
            "agreement_date": "2022-06-20",
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
        }
        assert response.json()["results"][0] == expected_ticket
        assert response.json()["count"] == 2

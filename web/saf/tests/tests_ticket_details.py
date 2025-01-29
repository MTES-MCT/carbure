from datetime import datetime

from django.urls import reverse

from core.models import Biocarburant, MatierePremiere, Pays
from saf.models import SafTicket, SafTicketSource
from saf.tests import TestCase


class SafTicketDetailsTest(TestCase):
    def setUp(self):
        super().setUp()
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

    def test_saf_ticket_details_nok(self):
        query = {"entity_id": self.entity.id}
        response = self.client.get(reverse("saf-tickets-detail", kwargs={"id": 43211111}), query)

        assert response.status_code == 404

    def test_saf_ticket_details_ok(self):
        query = {"entity_id": self.entity.id}
        response = self.client.get(reverse("saf-tickets-detail", kwargs={"id": 4321}), query)

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
            "supplier": self.entity.name,
            "client": self.ticket_client.name,
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
            "free_field": None,
            "client_comment": None,
            "parent_ticket_source": {
                "id": 1234,
                "carbure_id": "carbure-id-001",
                "total_volume": 30000.0,
                "assigned_volume": 0.0,
            },
            "shipping_method": None,
            "reception_airport": None,
            "consumption_type": None,
        }

        assert response.json() == expected_ticket

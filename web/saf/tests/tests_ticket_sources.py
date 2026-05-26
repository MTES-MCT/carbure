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
            feedstock=MatierePremiere.biofuel.get(code="HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2"),
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
            feedstock=MatierePremiere.biofuel.get(code="HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2"),
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
            "total_volume": 30000.0,
            "assigned_volume": 0.0,
            "biofuel": {
                "name": "Huiles co-traitées - Kérosène",
                "name_en": "",
                "code": "HCC",
            },
            "ghg_reduction": 65.0,
            "parent_ticket": None,
            "added_by": {
                "id": self.entity.id,
                "name": self.entity.name,
                "entity_type": self.entity.entity_type,
                "registration_id": self.entity.registration_id,
            },
        }

        expected_assigned_ticket = {
            "agreement_date": "2022-06-20",
            "assignment_period": 202201,
            "carbure_id": "carbure-id-t-001",
            "client": self.ticket_client.name,
            "id": 4321,
            "status": "PENDING",
            "volume": 30000.0,
        }

        data = response.json()["results"][0]

        for key, value in expected_ticket_source.items():
            self.assertEqual(data[key], value)

        self.assertEqual(len(data["assigned_tickets"]), 1)
        for key, value in expected_assigned_ticket.items():
            self.assertEqual(data["assigned_tickets"][0][key], value)

        self.assertEqual(response.json()["count"], 2)

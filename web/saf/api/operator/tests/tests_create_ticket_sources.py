import factory
from django.test import TestCase
from django.urls import reverse

from core.models import Biocarburant, Entity
from core.tests_utils import setup_current_user
from saf.models import SafTicket, SafTicketSource
from transactions.factories.carbure_lot import CarbureLotFactory


class SafCreateTicketSourcesTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/productionsites.json",
        "json/depots.json",
    ]

    def setUp(self):
        self.operator = Entity.objects.create(name="SAF Operator", entity_type=Entity.OPERATOR, has_saf=True)
        self.producer = Entity.objects.create(name="SAF Producer", entity_type=Entity.PRODUCER)
        self.airline = Entity.objects.create(name="SAF Airline", entity_type=Entity.AIRLINE)
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.operator, "ADMIN")])

        self.period = 202302
        saf = Biocarburant.objects.filter(code__in=["HVOC", "HOC", "HCC"])

        self.lots = CarbureLotFactory.create_batch(
            10,
            lot_status="ACCEPTED",
            correction_status="NO_PROBLEMO",
            year=2023,
            volume=100000.0,
            biofuel=factory.Iterator(saf),
            period=self.period,
            added_by=self.producer,
            carbure_producer=self.producer,
            carbure_supplier=self.producer,
            carbure_client=self.operator,
        )

    def test_create_ticket_sources_from_declaration(self):
        assert SafTicketSource.objects.count() == 0

        # declaration of the producer for the period
        self.client.post(
            reverse("transactions-declarations-validate"), {"entity_id": self.producer.id, "period": self.period}
        )

        assert SafTicketSource.objects.count() == 0

        # declaration of the operator for the period
        self.client.post(
            reverse("transactions-declarations-validate"), {"entity_id": self.operator.id, "period": self.period}
        )

        ticket_sources = SafTicketSource.objects.all()
        assert ticket_sources.count() == 10
        assert ticket_sources.values("parent_lot__id").distinct().count() == 10

        lots_by_id = {lot.id: lot for lot in self.lots}

        for ts in ticket_sources:
            parent_lot = lots_by_id.get(ts.parent_lot.id)
            assert ts.total_volume == parent_lot.volume
            assert ts.assigned_volume == 0.0

    def test_update_ticket_sources_from_redeclaration(self):
        # two-sided declaration
        self.client.post(
            reverse("transactions-declarations-validate"), {"entity_id": self.producer.id, "period": self.period}
        )
        self.client.post(
            reverse("transactions-declarations-validate"), {"entity_id": self.operator.id, "period": self.period}
        )

        first_ticket_source = SafTicketSource.objects.first()

        # operator creates tickets
        params = {
            "entity_id": self.operator.id,
            "ticket_source_id": first_ticket_source.id,
            "client_id": self.airline.id,
            "volume": 60000,
            "agreement_reference": "blabla",
            "agreement_date": "2023-11-24",
            "free_field": "",
            "assignment_period": 202311,
        }

        response = self.client.post(reverse("saf-operator-assign-ticket"), params)
        assert response.status_code == 200

        # check that ticket was created
        tickets = SafTicket.objects.all()
        assert tickets.count() == 1
        assert tickets.first().parent_ticket_source == first_ticket_source

        # check that ticket source was updated
        first_ticket_source.refresh_from_db()
        assert first_ticket_source.assigned_volume == 60000.0

        # operator invalidates its declaration
        self.client.post(
            reverse("transactions-declarations-invalidate"), {"entity_id": self.operator.id, "period": self.period}
        )

        # ticket sources still exist
        assert SafTicketSource.objects.count() == 10

        # check that ticket source was not updated
        first_ticket_source.refresh_from_db()
        assert first_ticket_source.assigned_volume == 60000.0

        # operator revalidates its declaration
        self.client.post(
            reverse("transactions-declarations-validate"), {"entity_id": self.operator.id, "period": self.period}
        )

        # check that ticket source was not updated
        first_ticket_source.refresh_from_db()
        assert first_ticket_source.assigned_volume == 60000.0

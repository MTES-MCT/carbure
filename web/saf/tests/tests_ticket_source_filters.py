from core.models import MatierePremiere, Pays
from core.tests_utils import FiltersActionTestMixin
from resources.factories.production_site import ProductionSiteFactory
from saf.factories import SafTicketFactory, SafTicketSourceFactory
from saf.models import SafTicket, SafTicketSource
from saf.tests import TestCase
from saf.views import SafTicketSourceViewSet
from transactions.factories.depot import DepotFactory


class SafTicketSourceFiltersTest(TestCase, FiltersActionTestMixin):
    def setUp(self):
        super().setUp()

        self.ble = MatierePremiere.objects.get(code="BLE")
        self.colza = MatierePremiere.objects.get(code="COLZA")
        self.hau = MatierePremiere.objects.get(code="HUILE_ALIMENTAIRE_USAGEE")
        self.hga = MatierePremiere.objects.get(code="HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2")
        self.fr = Pays.objects.create(code_pays="FR", name="France", name_en="France")
        self.psite = ProductionSiteFactory.create(name="Production Site 1")
        self.depot = DepotFactory.create(name="Depot 1")

        SafTicketSource.objects.all().delete()
        SafTicket.objects.all().delete()
        self.ticket_sources = [
            self.create_ticket_source(),
            self.create_ticket_source(feedstock=self.hga),
            self.create_ticket_source(feedstock=self.ble),
            self.create_ticket_source(feedstock=self.colza),
            self.create_ticket_source(delivery_period=202202),
            self.create_ticket_source(feedstock=self.hga, delivery_period=202202),
        ]

        first_id = self.ticket_sources[0].id

        SafTicket.objects.all().delete()
        self.ticket = SafTicketFactory.create(
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

        # create a ticket source with a parent ticket so we can check for the supplier
        self.create_ticket_source(parent_ticket=self.ticket)

    def create_ticket_source(self, **overrides):
        props = {
            "year": 2022,
            "delivery_period": 202201,
            "added_by_id": self.entity.id,
            "feedstock": self.hau,
            "assigned_volume": 0,
            "country_of_origin": self.fr,
            "carbure_production_site": self.psite,
            "origin_lot_site": self.depot,
            **overrides,
        }

        return SafTicketSourceFactory.create(**props)

    def test_ticket_source_filters(self):
        self.assertFilters(
            SafTicketSourceViewSet,
            {
                "added_by": [self.entity.name],
                "supplier": [self.entity.name],
                "client": [self.client1.name, self.client2.name],
                "feedstock": [self.ble.code, self.colza.code, self.hau.code, self.hga.code],
                "period": [202201, 202202],
                "year": [2022],
                "country_of_origin": [self.fr.code_pays],
                "production_site": [self.psite.name],
                "origin_depot": [self.depot.name],
            },
            entity=self.entity,
            ignore=["order_by"],
        )

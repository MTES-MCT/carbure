from core.models import MatierePremiere, Pays
from core.tests_utils import FiltersActionTestMixin
from resources.factories.production_site import ProductionSiteFactory
from saf.factories import SafTicketFactory
from saf.models import SafTicket
from saf.tests import TestCase
from saf.views import SafTicketViewSet
from transactions.factories.depot import DepotFactory


class SafTicketFiltersTest(TestCase, FiltersActionTestMixin):
    def setUp(self):
        super().setUp()

        self.hau = MatierePremiere.objects.get(code="HUILE_ALIMENTAIRE_USAGEE")
        self.hga = MatierePremiere.objects.get(code="HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2")
        self.fr = Pays.objects.create(code_pays="FR", name="France", name_en="France")
        self.psite = ProductionSiteFactory.create(name="Production Site 1")
        self.depot = DepotFactory.create(name="Depot 1")

        SafTicket.objects.all().delete()

        self.create_ticket()
        self.create_ticket(assignment_period=202202, client_id=self.client2.id, status=SafTicket.ACCEPTED)
        self.create_ticket(client_id=self.client2.id, feedstock=self.hga, status=SafTicket.PENDING)

    def create_ticket(self, **overrides):
        props = {
            "year": 2022,
            "assignment_period": 202201,
            "supplier_id": self.entity.id,
            "client_id": self.client1.id,
            "feedstock": self.hau,
            "status": SafTicket.PENDING,
            "country_of_origin": self.fr,
            "carbure_production_site": self.psite,
            "origin_lot_site": self.depot,
            **overrides,
        }

        return SafTicketFactory.create(**props)

    def test_ticket_filters_feedstock(self):
        self.assertFilters(
            SafTicketViewSet,
            {
                "status": [SafTicket.ACCEPTED, SafTicket.PENDING],
                "year": [2022],
                "supplier": [self.entity.name],
                "client": [self.client1.name, self.client2.name],
                "client_type": [self.client1.entity_type],
                "feedstock": [self.hau.code, self.hga.code],
                "period": [202201, 202202],
                "country_of_origin": [self.fr.code_pays],
                "production_site": [self.psite.name],
                "consumption_type": [],
                "reception_airport": [],
                "origin_depot": [self.depot.name],
            },
            entity=self.entity,
            ignore=["order_by"],
        )

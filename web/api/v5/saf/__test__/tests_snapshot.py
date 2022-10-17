from django.test import TestCase
from django.urls import reverse


from api.v4.tests_utils import setup_current_user
from core.models import Entity
from saf.factories import SafTicketSourceFactory, SafTicketFactory
from saf.models import SafTicketSource, SafTicket
from core.models import Biocarburant, MatierePremiere, Pays
from producers.models import ProductionSite


class SafSnapshotTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/productionsites.json",
    ]

    def setUp(self):
        # let's create a user with some rights
        self.entity = Entity.objects.filter(entity_type=Entity.OPERATOR)[0]
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, "ADMIN")])

        self.ticket_sources = [SafTicketSourceFactory.create() for _ in range(0, 100)]
        SafTicketSource.objects.bulk_create(self.ticket_sources)

        self.tickets = [SafTicketFactory.create() for _ in range(0, 100)]
        SafTicket.objects.bulk_create(self.tickets)

    def test_saf_snapshot(self):
        pass

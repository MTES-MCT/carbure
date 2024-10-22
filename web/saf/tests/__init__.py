from django.test import TestCase as DjangoTestCase

from core.models import Entity
from core.tests_utils import setup_current_user
from saf.factories import SafTicketFactory, SafTicketSourceFactory
from saf.models import SafTicket, SafTicketSource


class TestCase(DjangoTestCase):
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
        self.user = setup_current_user(
            self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, "ADMIN")]
        )
        
        self.client1 = Entity.objects.filter(entity_type=Entity.OPERATOR)[1]
        self.client2 = Entity.objects.filter(entity_type=Entity.OPERATOR)[2]

        SafTicketSource.objects.all().delete()
        self.ticket_source = SafTicketSourceFactory.create(
            added_by_id=self.entity.id,
            delivery_period=202202,
            total_volume=30000,
            assigned_volume=10000,
        )

        SafTicket.objects.all().delete()
        
        
        self.ticket = SafTicketFactory.create(
            supplier_id=self.entity.id,
            client_id=self.ticket_client.id,
            volume=10000,
            parent_ticket_source_id=self.ticket_source.id,
        )

        
        
from django.test import TestCase as DjangoTestCase
from django.urls import reverse

from core.models import Entity
from core.serializers import EntityPreviewSerializer
from core.tests_utils import setup_current_user


class SafClientsTest(DjangoTestCase):
    def setUp(self):
        super().setUp()
        self.airline = Entity.objects.create(name="Airline", entity_type=Entity.AIRLINE)
        self.saf_trader = Entity.objects.create(name="Saf Trader", entity_type=Entity.SAF_TRADER)
        self.user = setup_current_user(
            self, "tester@carbure.local", "Tester", "gogogo", [(self.airline, "ADMIN"), (self.saf_trader, "ADMIN")]
        )
        self.saf_operator = Entity.objects.create(name="Saf Operator", entity_type=Entity.OPERATOR, has_saf=True)
        self.operator = Entity.objects.create(name="Simple Operator", entity_type=Entity.OPERATOR)

    def tearDown(self) -> None:
        Entity.objects.all().delete()

    def test_saf_clients(self):
        expected_response = [EntityPreviewSerializer(self.saf_operator).data, EntityPreviewSerializer(self.saf_trader).data]
        query = {"entity_id": self.airline.id}

        response = self.client.get(reverse("clients-list"), query)
        json = response.json()

        assert response.status_code == 200
        assert json["count"] == 2
        assert json["results"] == expected_response

    def test_saf_trader_clients(self):
        query = {"entity_id": self.saf_trader.id}

        response = self.client.get(reverse("clients-list"), query)
        json = response.json()

        assert response.status_code == 200
        assert json["count"] == 1
        assert json["results"] == [EntityPreviewSerializer(self.airline).data]

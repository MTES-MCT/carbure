from core.models import Entity, GenericError
from django.db.models import Count
from django.test import TestCase
from django.urls import reverse
from api.v4.tests_utils import setup_current_user
from transactions.factories import CarbureLotFactory, CarbureStockFactory


def debug_errors(lot):
    errors = GenericError.objects.filter(lot=lot)
    for e in errors:
        print(e.error, e.field, e.value, e.extra)


class StocksFlowTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/productionsites.json",
    ]

    def setUp(self):
        self.producer = (
            Entity.objects.filter(entity_type=Entity.PRODUCER)
            .annotate(psites=Count("productionsite"))
            .filter(psites__gt=0)[0]
        )

        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "gogogo",
            [(self.producer, "RW")],
        )

    def test_get_stocks(self):
        parent_lot = CarbureLotFactory.create()
        CarbureStockFactory.create(parent_lot=parent_lot, carbure_client=self.producer)

        query = {"entity_id": self.producer.id}

        response = self.client.get(reverse("transactions-stocks"), query)
        stocks_data = response.json()["data"]
        self.assertEqual(len(stocks_data["stocks"]), 1)
        self.assertEqual(stocks_data["stocks"][0]["carbure_client"]["id"], self.producer.id)

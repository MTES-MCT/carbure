import datetime
import json
import random

from api.v4.tests_utils import setup_current_user
from core.models import Entity
from django.db.models import Count
from django.test import TestCase
from django.urls import reverse
from transactions.factories import CarbureLot, CarbureLotFactory, CarbureStock, CarbureStockFactory, Depot


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
        parent_lot = CarbureLotFactory.create(
            lot_status="ACCEPTED",
            carbure_producer=self.producer,
            carbure_supplier=self.producer,
            added_by=self.producer,
        )

        CarbureStockFactory.create(
            parent_lot=parent_lot,
            carbure_client=self.producer,
        )

        query = {"entity_id": self.producer.id}

        response = self.client.get(reverse("transactions-stocks"), query)
        stocks_data = response.json()["data"]
        self.assertEqual(len(stocks_data["stocks"]), 1)
        self.assertEqual(stocks_data["stocks"][0]["carbure_client"]["id"], self.producer.id)

    def test_get_stocks_summary(self):
        parent_lot = CarbureLotFactory.create(lot_status="ACCEPTED")
        CarbureStockFactory.create(
            parent_lot=parent_lot,
            carbure_client=self.producer,
            remaining_volume=1000,
        )
        query = {"entity_id": self.producer.id}
        response = self.client.get(reverse("transactions-stocks-summary"), query)
        summary_data = response.json()["data"]
        self.assertEqual(summary_data["total_remaining_volume"], 1000)

    def test_get_stocks_details(self):
        parent_lot = CarbureLotFactory.create(
            lot_status="ACCEPTED",
        )
        stock = CarbureStockFactory.create(
            parent_lot=parent_lot,
            carbure_client=self.producer,
            remaining_volume=1000,
        )
        query = {"entity_id": self.producer.id, "stock_id": stock.id}
        response = self.client.get(reverse("transactions-stocks-details"), query)
        stock_data = response.json()["data"]["stock"]
        self.assertEqual(stock_data["remaining_volume"], 1000)

    def stock_split(self, payload, fail=False):
        response = self.client.post(
            reverse("transactions-stocks-split"), {"entity_id": self.producer.id, "payload": json.dumps(payload)}
        )
        if not fail:
            self.assertEqual(response.status_code, 200)
            data = response.json()["data"]
            lot_id = data[0]
            lot = CarbureLot.objects.get(id=lot_id)
            return lot
        else:
            self.assertEqual(response.status_code, 400)
            return None

    def test_stock_split(self):
        parent_lot = CarbureLotFactory.create(
            carbure_client_id=self.producer.id,
            volume=500000,
            delivery_type=CarbureLot.STOCK,
            lot_status="ACCEPTED",
            carbure_producer=self.producer,
        )

        self.assertEqual(parent_lot.lot_status, CarbureLot.ACCEPTED)
        self.assertEqual(parent_lot.delivery_type, CarbureLot.STOCK)
        stock = CarbureStockFactory.create(parent_lot=parent_lot, carbure_client=self.producer, remaining_volume=50000)

        today = datetime.date.today().strftime("%d/%m/%Y")

        # 1: split 10000L for export
        payload = {
            "volume": 10000,
            "stock_id": stock.carbure_id,
            "delivery_date": today,
            "delivery_site_country_id": "DE",
            "delivery_type": "EXPORT",
        }
        lot = self.stock_split([payload])
        self.assertEqual(lot.lot_status, CarbureLot.DRAFT)
        self.assertEqual(lot.delivery_type, CarbureLot.EXPORT)

        # 2: split 10000L for RFC
        payload = {
            "volume": 10000,
            "stock_id": stock.carbure_id,
            "delivery_date": today,
            "delivery_site_country_id": "FR",
            "delivery_type": "RFC",
        }
        lot = self.stock_split([payload])
        self.assertEqual(lot.lot_status, CarbureLot.DRAFT)
        self.assertEqual(lot.delivery_type, CarbureLot.RFC)

        # 3: split 10000L for blending
        depots = Depot.objects.all()
        trader = Entity.objects.filter(entity_type=Entity.TRADER)[0]
        payload = {
            "volume": 10000,
            "stock_id": stock.carbure_id,
            "delivery_date": today,
            "delivery_site_country_id": "FR",
            "delivery_type": "BLENDING",
            "transport_document_reference": "FR-BLENDING-TEST",
            "carbure_delivery_site_id": random.choice(depots).depot_id,
            "carbure_client_id": trader.id,
        }
        lot = self.stock_split([payload])
        self.assertEqual(lot.lot_status, CarbureLot.DRAFT)
        self.assertEqual(lot.delivery_type, CarbureLot.BLENDING)

        # 4: split 10000L for carbure_client
        operator = Entity.objects.filter(entity_type=Entity.OPERATOR)[0]
        payload = {
            "volume": 10000,
            "stock_id": stock.carbure_id,
            "delivery_date": today,
            "delivery_site_country_id": "FR",
            "transport_document_reference": "FR-SPLIT-SEND-TEST",
            "carbure_delivery_site_id": random.choice(depots).depot_id,
            "carbure_client_id": operator.id,
        }
        lot = self.stock_split([payload])
        self.assertEqual(lot.lot_status, CarbureLot.DRAFT)
        self.assertEqual(lot.delivery_type, CarbureLot.UNKNOWN)

        # 5: split 10000L for unknown_client
        payload = {
            "volume": 10000,
            "stock_id": stock.carbure_id,
            "delivery_date": today,
            "delivery_site_country_id": "DE",
            "transport_document_reference": "FR-BLENDING-TEST",
            "unknown_client": "FOREIGN CLIENT",
        }
        lot = self.stock_split([payload])

        self.assertEqual(lot.lot_status, CarbureLot.DRAFT)
        self.assertEqual(lot.delivery_type, CarbureLot.UNKNOWN)
        stock = CarbureStock.objects.get(parent_lot=parent_lot)
        self.assertEqual(stock.remaining_volume, 0)

        # 6: split 10000L for unknown_client - not enough volume
        payload = {
            "volume": 10000,
            "stock_id": stock.carbure_id,
            "delivery_date": today,
            "delivery_site_country_id": "DE",
            "transport_document_reference": "FR-BLENDING-TEST",
            "unknown_client": "FOREIGN CLIENT",
        }
        failed = self.stock_split([payload], fail=True)
        self.assertEqual(failed, None)

        # 7: update a draft, check that volume is correctly adjusted
        data = {
            "lot_id": lot.id,
            "volume": 9000,
            "entity_id": self.producer.id,
            "delivery_date": today,
            "delivery_site_country_id": "DE",
            "transport_document_reference": "FR-UPDATED-DAE",
            "unknown_client": "FOREIGN CLIENT",
        }
        response = self.client.post(reverse("transactions-lots-update"), data)
        self.assertEqual(response.status_code, 200)
        lot = CarbureLot.objects.get(id=lot.id)
        self.assertEqual(lot.volume, 9000)  # volume updated
        self.assertEqual(lot.transport_document_reference, "FR-UPDATED-DAE")
        stock = CarbureStock.objects.get(id=lot.parent_stock.id)
        self.assertEqual(stock.remaining_volume, 1000)

        # 8 update a draft with more than volume left, ensure lot and stock are not updated
        data["volume"] = 11000
        response = self.client.post(reverse("transactions-lots-update"), data)
        self.assertEqual(response.status_code, 200)
        lot = CarbureLot.objects.get(id=lot.id)
        self.assertEqual(lot.volume, 9000)  # volume NOT updated
        stock = CarbureStock.objects.get(id=lot.parent_stock.id)
        self.assertEqual(stock.remaining_volume, 1000)

        # 9: delete a draft, check that volume is correctly re-credited
        response = self.client.post(
            reverse("api-v4-delete-lots"), {"entity_id": self.producer.id, "selection": [lot.id]}
        )
        self.assertEqual(response.status_code, 200)
        stock = CarbureStock.objects.get(parent_lot=parent_lot)
        self.assertEqual(stock.remaining_volume, 10000)

    def test_stock_flush(self):
        parent_lot = CarbureLotFactory.create(
            carbure_client_id=self.producer.id,
            volume=100000,
            delivery_type=CarbureLot.STOCK,
            lot_status="ACCEPTED",
        )

        # Flush
        stock = CarbureStockFactory.create(parent_lot=parent_lot, carbure_client=self.producer, remaining_volume=1000)
        stock.save()  # HACK to avoid `generate_carbure_id` later
        query = {"entity_id": self.producer.id, "stock_ids": [stock.id]}
        response = self.client.post(reverse("transactions-stocks-flush"), query)
        status = response.json()["status"]
        self.assertEqual(status, "success")

        # Cannot flush a stock with a remaining volume greater than 1% => 5% in deed
        stock = CarbureStockFactory.create(parent_lot=parent_lot, carbure_client=self.producer, remaining_volume=5001)
        stock.save()  # HACK to avoid `generate_carbure_id` later
        query = {"entity_id": self.producer.id, "stock_ids": [stock.id]}
        response = self.client.post(reverse("transactions-stocks-flush"), query)
        status = response.json()["status"]
        self.assertEqual(status, "error")

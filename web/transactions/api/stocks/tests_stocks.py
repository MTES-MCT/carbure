import datetime
import json
import random

from django.db.models import Count
from django.test import TestCase
from django.urls import reverse

from core.models import Biocarburant, CarbureLot, CarbureStock, CarbureStockTransformation, Entity
from core.tests_utils import setup_current_user
from transactions.factories import CarbureLotFactory, CarbureStockFactory
from transactions.models import Depot


class StocksFlowTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/productionsites.json",
        "json/entities_sites.json",
    ]

    def setUp(self):
        self.producer = (
            Entity.objects.filter(entity_type=Entity.PRODUCER)
            .annotate(psites=Count("entitysite__site"))
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
        assert len(stocks_data["stocks"]) == 1
        assert stocks_data["stocks"][0]["carbure_client"]["id"] == self.producer.id

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
        assert summary_data["total_remaining_volume"] == 1000

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
        assert stock_data["remaining_volume"] == 1000

    def stock_split(self, payload, fail=False):
        response = self.client.post(
            reverse("transactions-stocks-split"),
            {"entity_id": self.producer.id, "payload": json.dumps(payload)},
        )
        print("response : ", response.json(), response.status_code)
        if not fail:
            assert response.status_code == 200
            data = response.json()["data"]
            lot_id = data[0]
            lot = CarbureLot.objects.get(id=lot_id)
            return lot
        else:
            assert response.status_code == 400
            return None

    def test_stock_split(self):
        parent_lot = CarbureLotFactory.create(
            carbure_client_id=self.producer.id,
            volume=500000,
            delivery_type=CarbureLot.STOCK,
            lot_status="ACCEPTED",
            carbure_producer=self.producer,
        )

        assert parent_lot.lot_status == CarbureLot.ACCEPTED
        assert parent_lot.delivery_type == CarbureLot.STOCK
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
        assert lot.lot_status == CarbureLot.DRAFT
        assert lot.delivery_type == CarbureLot.EXPORT

        # 2: split 10000L for RFC
        payload = {
            "volume": 10000,
            "stock_id": stock.carbure_id,
            "delivery_date": today,
            "delivery_site_country_id": "FR",
            "delivery_type": "RFC",
        }
        lot = self.stock_split([payload])
        assert lot.lot_status == CarbureLot.DRAFT
        assert lot.delivery_type == CarbureLot.RFC

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
            "carbure_delivery_site_id": random.choice(depots).customs_id,
            "carbure_client_id": trader.id,
        }
        print("payload : ", payload)
        lot = self.stock_split([payload])
        assert lot.lot_status == CarbureLot.DRAFT
        assert lot.delivery_type == CarbureLot.BLENDING

        # 4: split 10000L for carbure_client
        operator = Entity.objects.filter(entity_type=Entity.OPERATOR)[0]
        payload = {
            "volume": 10000,
            "stock_id": stock.carbure_id,
            "delivery_date": today,
            "delivery_site_country_id": "FR",
            "transport_document_reference": "FR-SPLIT-SEND-TEST",
            "carbure_delivery_site_id": random.choice(depots).customs_id,
            "carbure_client_id": operator.id,
        }
        lot = self.stock_split([payload])
        assert lot.lot_status == CarbureLot.DRAFT
        assert lot.delivery_type == CarbureLot.UNKNOWN

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

        assert lot.lot_status == CarbureLot.DRAFT
        assert lot.delivery_type == CarbureLot.UNKNOWN
        stock = CarbureStock.objects.get(parent_lot=parent_lot)
        assert stock.remaining_volume == 0

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
        assert failed is None

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
        assert response.status_code == 200
        lot = CarbureLot.objects.get(id=lot.id)
        assert lot.volume == 9000  # volume updated
        assert lot.transport_document_reference == "FR-UPDATED-DAE"
        stock = CarbureStock.objects.get(id=lot.parent_stock.id)
        assert stock.remaining_volume == 1000

        # 8 update a draft with more than volume left, ensure lot and stock are not updated
        data["volume"] = 11000
        response = self.client.post(reverse("transactions-lots-update"), data)
        assert response.status_code == 200
        lot = CarbureLot.objects.get(id=lot.id)
        assert lot.volume == 9000  # volume NOT updated
        stock = CarbureStock.objects.get(id=lot.parent_stock.id)
        assert stock.remaining_volume == 1000

        # 9: delete a draft, check that volume is correctly re-credited
        response = self.client.post(
            reverse("transactions-lots-delete"),
            {"entity_id": self.producer.id, "selection": [lot.id]},
        )
        assert response.status_code == 200
        stock = CarbureStock.objects.get(parent_lot=parent_lot)
        assert stock.remaining_volume == 10000

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
        assert status == "success"

        # Cannot flush a stock with a remaining volume greater than 1% => 5% in deed
        stock = CarbureStockFactory.create(parent_lot=parent_lot, carbure_client=self.producer, remaining_volume=5001)
        stock.save()  # HACK to avoid `generate_carbure_id` later
        query = {"entity_id": self.producer.id, "stock_ids": [stock.id]}
        response = self.client.post(reverse("transactions-stocks-flush"), query)
        status = response.json()["status"]
        assert status == "error"

    def test_stock_transformation(self):
        eth = Biocarburant.objects.get(code="ETH")

        parent_lot = CarbureLotFactory.create(
            carbure_client_id=self.producer.id,
            volume=200_000,
            delivery_type=CarbureLot.STOCK,
            biofuel=eth,
            lot_status="ACCEPTED",
        )

        source_stock = CarbureStockFactory.create(
            parent_lot=parent_lot,
            carbure_client=self.producer,
            remaining_volume=200_000,
            biofuel=eth,
        )

        body = {
            "entity_id": self.producer.id,
            "payload": json.dumps(
                [
                    {
                        "stock_id": source_stock.id,
                        "transformation_type": "ETH_ETBE",
                        "volume_ethanol": 90_000,
                        "volume_etbe": 200_000,
                        "volume_denaturant": 10_000,
                        "volume_etbe_eligible": 100_000,
                    }
                ]
            ),
        }

        # transform part of stock into etbe
        self.client.post(reverse("transactions-stocks-transform"), body)

        source_stock.refresh_from_db()

        assert source_stock.remaining_volume == 110000

        transform = source_stock.source_stock.select_related("dest_stock").first()
        assert transform.volume_deducted_from_source == 90000

        dest_stock = CarbureStock.objects.get(parent_transformation=transform)
        assert dest_stock.biofuel.code == "ETBE"
        assert dest_stock.remaining_volume == 200000

        # cancel transform
        body = {"entity_id": self.producer.id, "stock_ids": [dest_stock.id]}
        self.client.post(reverse("transactions-stocks-cancel-transformation"), body)

        transform_still_exists = CarbureStockTransformation.objects.filter(id=transform.id).count() > 0
        assert transform_still_exists is False

        dest_stock_still_exists = CarbureStock.objects.filter(id=dest_stock.id).count() > 0
        assert dest_stock_still_exists is False

        source_stock.refresh_from_db()
        assert source_stock.remaining_volume == 200000

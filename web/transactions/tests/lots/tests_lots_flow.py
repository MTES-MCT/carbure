from django.urls import reverse

from core.carburetypes import CarbureError
from core.models import CarbureLot, CarbureStock
from transactions.models import YearConfig
from transactions.tests.lots import TestCase
from transactions.tests.tests_utils import get_lot


class LotsFlowTest(TestCase):
    def test_create_draft(self, **kwargs):
        YearConfig.objects.create(year=2018, locked=True)  # 2021 is the right year
        lot = self.create_draft(**kwargs)
        assert lot.lot_status == CarbureLot.DRAFT

    def test_create_draft_on_locked_year(self, **kwargs):
        YearConfig.objects.create(year=2021, locked=True)
        lot = get_lot(self.created_by)
        lot.update(kwargs)
        response = self.client.post(reverse("v2-transactions-lots-add") + f"?entity_id={self.created_by.id}", lot)
        assert response.status_code == 200
        lot_id = response.json()["id"]

        response = self.client.get(
            reverse("v2-transactions-lots-detail", kwargs={"id": lot_id}),
            {"lot_id": lot_id, "entity_id": self.created_by.id},
        )
        errors = response.json()["errors"]
        assert errors[0]["error"] == CarbureError.YEAR_LOCKED

    def test_update_lot(self):
        YearConfig.objects.create(year=2018, locked=True)
        lotdata = get_lot(entity=self.created_by)
        lot = self.create_draft(lot=lotdata)
        lotdata["lot_id"] = lot.id
        lotdata["volume"] = 42000

        lotdata["delivery_date"] = "2022-01-01"
        response = self.client.post(
            reverse("v2-transactions-lots-update-lot", kwargs={"id": lot.id}) + f"?entity_id={self.created_by.id}",
            lotdata,
        )
        assert response.status_code == 200
        lot = CarbureLot.objects.get(id=lot.id)
        assert lot.volume == 42000
        assert lot.year == 2022

    def test_delete_lot(self):
        lot = self.create_draft()
        response = self.client.post(
            reverse("v2-transactions-lots-delete") + f"?entity_id={self.created_by.id}",
            {"entity_id": self.created_by.id, "selection": [lot.id]},
        )
        assert response.status_code == 200
        assert not CarbureLot.objects.filter(id=lot.id).exists()

        lot = self.send_lot(self.create_draft())
        response = self.client.post(
            reverse("v2-transactions-lots-delete") + f"?entity_id={self.created_by.id}",
            {"entity_id": self.created_by.id, "selection": [lot.id]},
        )  # cannot delete a lot not in draft
        assert response.status_code == 200
        lot.refresh_from_db()
        assert lot.lot_status == CarbureLot.DELETED

        lot = self.create_draft()
        response = self.client.post(
            reverse("v2-transactions-lots-delete") + f"?entity_id={self.trader.id}",
            {"entity_id": self.trader.id, "selection": [lot.id]},
        )  # cannot delete someone else's lot
        assert response.status_code == 400

    def test_duplicate_lot(self):
        lot = self.create_draft()
        response = self.client.get(
            reverse("v2-transactions-lots-duplicate", kwargs={"id": lot.id}) + f"?entity_id={self.created_by.id}",
        )
        assert response.status_code == 200
        response = self.client.get(
            reverse("v2-transactions-lots-duplicate", kwargs={"id": lot.id}) + f"?entity_id={self.trader.id}"
        )
        assert response.status_code == 403

    def test_send(self):
        lot = self.create_draft()
        lot = self.send_lot(lot)
        assert lot.lot_status == CarbureLot.PENDING

    def test_accept_in_stock(self):
        lot = self.create_draft(carbure_client_id=self.trader.id)
        lot = self.send_lot(lot)

        response = self.client.post(
            reverse("v2-transactions-lots-accept-in-stock") + f"?entity_id={self.trader.id}",
            {"entity_id": self.trader.id, "selection": [lot.id]},
        )
        assert response.status_code == 200
        lot = CarbureLot.objects.get(id=lot.id)
        assert lot.lot_status == CarbureLot.ACCEPTED
        assert lot.delivery_type == CarbureLot.STOCK
        stock = CarbureStock.objects.filter(parent_lot=lot).count()
        assert stock == 1

    def test_accept_rfc(self):
        lot = self.create_draft(carbure_client_id=self.operator.id)
        lot = self.send_lot(lot)
        assert lot.lot_status == CarbureLot.PENDING
        assert lot.delivery_type == CarbureLot.UNKNOWN
        response = self.client.post(
            reverse("v2-transactions-lots-accept-rfc") + f"?entity_id={self.operator.id}",
            {"entity_id": self.operator.id, "selection": [lot.id]},
        )
        assert response.status_code == 200
        lot = CarbureLot.objects.get(id=lot.id)
        assert lot.lot_status == CarbureLot.ACCEPTED
        assert lot.delivery_type == CarbureLot.RFC

    def test_send_rfc(self):
        lot = self.create_draft(unknown_client="CLIENT MAC", delivery_type="RFC", carbure_client_id="")
        lot = self.send_lot(lot)
        assert lot.lot_status == CarbureLot.ACCEPTED
        assert lot.delivery_type == CarbureLot.RFC

    def test_accept_trading_to_carbure_client(self):
        lot = self.create_draft(carbure_client_id=self.trader.id)
        lot = self.send_lot(lot)
        assert lot.lot_status == CarbureLot.PENDING
        assert lot.delivery_type == CarbureLot.UNKNOWN

        response = self.client.post(
            reverse("v2-transactions-lots-accept-trading") + f"?entity_id={self.trader.id}",
            {
                "entity_id": self.trader.id,
                "selection": [lot.id],
                "client_entity_id": self.operator.id,
            },
        )
        assert response.status_code == 200
        lot = CarbureLot.objects.get(id=lot.id)
        assert lot.lot_status == CarbureLot.ACCEPTED
        assert lot.delivery_type == CarbureLot.TRADING
        child = CarbureLot.objects.get(parent_lot=lot)
        assert child.lot_status == CarbureLot.PENDING
        assert child.delivery_type == CarbureLot.UNKNOWN

    def test_accept_trading_to_unknown_client(self):
        lot = self.create_draft(carbure_client_id=self.trader.id)
        lot = self.send_lot(lot)
        assert lot.lot_status == CarbureLot.PENDING
        assert lot.delivery_type == CarbureLot.UNKNOWN

        response = self.client.post(
            reverse("v2-transactions-lots-accept-trading") + f"?entity_id={self.trader.id}",
            {
                "entity_id": self.trader.id,
                "selection": [lot.id],
                "unknown_client": "TRADER CLIENT",
            },
        )
        assert response.status_code == 200
        lot = CarbureLot.objects.get(id=lot.id)
        assert lot.lot_status == CarbureLot.ACCEPTED
        assert lot.delivery_type == CarbureLot.TRADING
        child = CarbureLot.objects.get(parent_lot=lot)
        assert child.lot_status == CarbureLot.ACCEPTED
        assert child.delivery_type == CarbureLot.UNKNOWN

    def test_accept_processing(self):
        lot = self.create_draft(carbure_client_id=self.trader.id)
        lot = self.send_lot(lot)
        assert lot.lot_status == CarbureLot.PENDING
        assert lot.delivery_type == CarbureLot.UNKNOWN

        response = self.client.post(
            reverse("v2-transactions-lots-accept-processing") + f"?entity_id={self.trader.id}",
            {
                "entity_id": self.trader.id,
                "selection": [lot.id],
                "processing_entity_id": self.operator.id,
            },
        )
        assert response.status_code == 200
        lot = CarbureLot.objects.get(id=lot.id)
        assert lot.lot_status == CarbureLot.ACCEPTED
        assert lot.delivery_type == CarbureLot.PROCESSING
        child = CarbureLot.objects.get(parent_lot=lot)
        assert child.lot_status == CarbureLot.PENDING
        assert child.delivery_type == CarbureLot.UNKNOWN

    def test_accept_blending(self):
        lot = self.create_draft(carbure_client_id=self.operator.id)
        lot = self.send_lot(lot)
        assert lot.lot_status == CarbureLot.PENDING
        assert lot.delivery_type == CarbureLot.UNKNOWN
        response = self.client.post(
            reverse("v2-transactions-lots-accept-blending") + f"?entity_id={self.operator.id}",
            {"entity_id": self.operator.id, "selection": [lot.id]},
        )
        assert response.status_code == 200
        lot = CarbureLot.objects.get(id=lot.id)
        assert lot.lot_status == CarbureLot.ACCEPTED
        assert lot.delivery_type == CarbureLot.BLENDING

    def test_accept_export(self):
        lot = self.create_draft(carbure_client_id=self.operator.id)
        lot = self.send_lot(lot)
        assert lot.lot_status == CarbureLot.PENDING
        assert lot.delivery_type == CarbureLot.UNKNOWN
        response = self.client.post(
            reverse("v2-transactions-lots-accept-export") + f"?entity_id={self.operator.id}",
            {"entity_id": self.operator.id, "selection": [lot.id]},
        )
        assert response.status_code == 200
        lot = CarbureLot.objects.get(id=lot.id)
        assert lot.lot_status == CarbureLot.ACCEPTED
        assert lot.delivery_type == CarbureLot.EXPORT

    def test_accept_direct_delivery(self):
        lot = self.create_draft(carbure_client_id=self.operator.id)
        lot = self.send_lot(lot)
        assert lot.lot_status == CarbureLot.PENDING
        assert lot.delivery_type == CarbureLot.UNKNOWN
        response = self.client.post(
            reverse("v2-transactions-lots-accept-direct-delivery") + f"?entity_id={self.operator.id}",
            {"entity_id": self.operator.id, "selection": [lot.id]},
        )
        assert response.status_code == 200
        lot = CarbureLot.objects.get(id=lot.id)
        assert lot.lot_status == CarbureLot.ACCEPTED
        assert lot.delivery_type == CarbureLot.DIRECT

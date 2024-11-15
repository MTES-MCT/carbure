from django.db.models import Count
from django.test import TestCase
from django.urls import reverse

from core.carburetypes import CarbureError
from core.models import CarbureLot, Entity
from core.tests_utils import setup_current_user
from transactions.models import YearConfig
from transactions.tests.tests_utils import get_lot


class LotCorrectionTest(TestCase):
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
        self.trader = Entity.objects.filter(entity_type=Entity.TRADER)[0]
        self.trader.default_certificate = "TRADER_CERTIFICATE"
        self.trader.save()
        self.operator = Entity.objects.filter(entity_type=Entity.OPERATOR)[0]

        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "gogogo",
            [
                (self.producer, "ADMIN"),
                (self.trader, "ADMIN"),
                (self.operator, "ADMIN"),
            ],
        )

    def prepare_lot(self, supplier, client=None, **kwargs):
        lot_data = get_lot(supplier, **kwargs)
        lot_data["carbure_supplier_id"] = supplier.id
        lot_data["carbure_client_id"] = client.id if client else self.trader.id

        add_response = self.client.post(reverse("v2-transactions-lots-add") + f"?entity_id={supplier.id}", lot_data)
        assert add_response.status_code == 200

        lot_id = add_response.json()["id"]

        send_response = self.client.post(
            reverse("v2-transactions-lots-send") + f"?entity_id={supplier.id}",
            {"entity_id": supplier.id, "selection": [lot_id]},
        )
        assert send_response.status_code == 200

        return CarbureLot.objects.get(id=lot_id)

    def request_fix(self, lot, entity):
        response = self.client.post(
            reverse("v2-transactions-lots-request-fix") + f"?entity_id={entity.id}",
            {"entity_id": entity.id, "lot_ids": [lot.id]},
        )
        assert response.status_code == 200
        lot = CarbureLot.objects.get(id=lot.id)
        return lot

    def submit_fix(self, lot, entity):
        response = self.client.post(
            reverse("v2-transactions-lots-submit-fix") + f"?entity_id={entity.id}",
            {"entity_id": entity.id, "lot_ids": [lot.id]},
        )
        assert response.status_code == 200
        lot = CarbureLot.objects.get(id=lot.id)
        return lot

    def approve_fix(self, lot, entity):
        response = self.client.post(
            reverse("v2-transactions-lots-approve-fix") + f"?entity_id={entity.id}",
            {"entity_id": entity.id, "lot_ids": [lot.id]},
        )
        assert response.status_code == 200
        lot = CarbureLot.objects.get(id=lot.id)
        return lot

    def test_recall_and_update(self):
        lot = self.prepare_lot(self.producer)
        assert lot.correction_status == CarbureLot.NO_PROBLEMO
        assert lot.lot_status == CarbureLot.PENDING
        lot = self.request_fix(lot, self.producer)
        assert lot.correction_status == CarbureLot.IN_CORRECTION
        assert lot.lot_status == CarbureLot.PENDING
        response = self.client.post(
            reverse("v2-transactions-lots-update-lot", kwargs={"id": lot.id}) + f"?entity_id={self.producer.id}",
            {"entity_id": self.producer.id, "volume": 42000},
        )

        assert response.status_code == 200
        lot = CarbureLot.objects.get(id=lot.id)
        assert lot.volume == 42000

    def test_simple_correction(self):
        YearConfig.objects.create(year=2020, locked=True)

        lot = self.prepare_lot(self.producer, self.trader)
        assert lot.lot_status == CarbureLot.PENDING
        assert lot.correction_status == CarbureLot.NO_PROBLEMO

        # client requests correction
        lot = self.request_fix(lot, self.trader)
        assert lot.lot_status == CarbureLot.PENDING
        assert lot.correction_status == CarbureLot.IN_CORRECTION

        # we update
        response = self.client.post(
            reverse("v2-transactions-lots-update-lot", kwargs={"id": lot.id}) + f"?entity_id={self.producer.id}",
            {"entity_id": self.producer.id, "volume": 42000},
        )
        assert response.status_code == 200

        lot = CarbureLot.objects.get(id=lot.id)
        assert lot.volume == 42000

        # and mark as fixed
        lot = self.submit_fix(lot, self.producer)
        assert lot.correction_status == CarbureLot.FIXED

        # as client, accept fix
        lot = self.approve_fix(lot, self.trader)
        assert lot.correction_status == CarbureLot.NO_PROBLEMO
        assert lot.lot_status == CarbureLot.PENDING

        # finally, accept lot
        response = self.client.post(
            reverse("v2-transactions-lots-accept-in-stock") + f"?entity_id={self.trader.id}",
            {"entity_id": self.trader.id, "selection": [lot.id]},
        )
        assert response.status_code == 200

        lot = CarbureLot.objects.get(id=lot.id)
        assert lot.correction_status == CarbureLot.NO_PROBLEMO
        assert lot.lot_status == CarbureLot.ACCEPTED

    def test_simple_correction_on_locked_year(self):
        lot = self.prepare_lot(self.producer, self.trader)

        YearConfig.objects.create(year=2021, locked=True)

        # client requests correction
        response = self.client.post(
            reverse("v2-transactions-lots-request-fix") + f"?entity_id={self.producer.id}",
            {"entity_id": self.producer.id, "lot_ids": [lot.id]},
        )
        assert response.status_code == 400
        assert response.json()["message"] == CarbureError.YEAR_LOCKED

    # check that the owner can edit everything on a root lot
    def test_full_owner_correction(self):
        pass

    # check that an entity can update durability info on a lot which's root owner is also this entity
    def test_ancestor_owner_correction(self):
        pass

    # check that the client cannot edit anything on a lot they didn't create
    def test_client_correction(self):
        pass

    # check that an entity can only update delivery info on a received lot they transferred
    def test_transfer_correction(self):
        pass

    # check that an entity can update everything on a lot duplicated for trading purpose
    def test_auto_trading_correction(self):
        pass

    # check that an entity can update transport fields on a lot extracted from owned stock
    def test_stock_correction(self):
        pass

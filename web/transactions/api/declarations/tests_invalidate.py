from django.test import TestCase
from django.urls import reverse

from core.carburetypes import CarbureError
from core.models import CarbureLot, Entity
from core.tests_utils import setup_current_user
from transactions.factories import CarbureLotFactory
from transactions.models import YearConfig


class InvalidateDeclarationTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/productionsites.json",
    ]

    def setUp(self):
        self.entity = Entity.objects.filter(entity_type=Entity.OPERATOR)[0]
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, "ADMIN")])

        CarbureLot.objects.all().delete()

        # create sent lots
        CarbureLotFactory.create_batch(
            50,
            lot_status=CarbureLot.FROZEN,
            correction_status=CarbureLot.NO_PROBLEMO,
            carbure_supplier=self.entity,
            carbure_client=None,
            period=202201,
            year=2022,
            declared_by_supplier=True,
            declared_by_client=True,
        )

        # create received lots
        CarbureLotFactory.create_batch(
            50,
            lot_status=CarbureLot.FROZEN,
            correction_status=CarbureLot.NO_PROBLEMO,
            carbure_client=self.entity,
            carbure_supplier=None,
            period=202201,
            year=2022,
            declared_by_supplier=True,
            declared_by_client=True,
        )

    def get_entity_lots(self, **kwargs):
        sent_lots = CarbureLot.objects.filter(carbure_supplier=self.entity, **kwargs)
        received_lots = CarbureLot.objects.filter(carbure_client=self.entity, **kwargs)
        return sent_lots, received_lots

    def test_invalidate_declaration(self):
        YearConfig.objects.create(year=2021, locked=True)

        query = {
            "entity_id": self.entity.id,
            "period": 202201,
        }

        response = self.client.post(reverse("transactions-declarations-invalidate"), query)

        assert response.status_code == 200
        assert response.json()["status"] == "success"

        sent_lots, received_lots = self.get_entity_lots(lot_status=CarbureLot.ACCEPTED)

        undeclared_sent_lots = sent_lots.filter(
            declared_by_supplier=False,
            declared_by_client=False,
        )

        assert undeclared_sent_lots.count() == 50

        undeclared_received_lots = received_lots.filter(
            declared_by_supplier=False,
            declared_by_client=False,
        )

        assert undeclared_received_lots.count() == 50

    def test_invalidate_declaration_on_locked_year(self):
        YearConfig.objects.create(year=2021, locked=True)

        query = {
            "entity_id": self.entity.id,
            "period": 202101,
        }

        response = self.client.post(reverse("transactions-declarations-invalidate"), query)
        assert response.status_code == 400
        assert response.json()["status"] == "error"
        assert response.json()["error"] == CarbureError.YEAR_LOCKED

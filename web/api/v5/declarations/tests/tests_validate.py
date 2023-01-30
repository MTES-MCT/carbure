import traceback

from django.test import TestCase
from django.urls import reverse

from core.tests_utils import setup_current_user
from core.models import Entity, CarbureLot
from lots.factory import CarbureLotFactory


class ValidateDeclarationTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/productionsites.json",
    ]

    def setUp(self):
        self.entity = Entity.objects.filter(entity_type=Entity.TRADER)[0]
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, "ADMIN")])

        CarbureLot.objects.all().delete()

        # create sent lots
        CarbureLotFactory.create_batch(
            50,
            lot_status=CarbureLot.ACCEPTED,
            correction_status=CarbureLot.NO_PROBLEMO,
            carbure_supplier=self.entity,
            carbure_client=None,
            period=202201,
            year=2022,
            declared_by_supplier=False,
            declared_by_client=True,
        )

        # create received lots
        CarbureLotFactory.create_batch(
            50,
            lot_status=CarbureLot.ACCEPTED,
            correction_status=CarbureLot.NO_PROBLEMO,
            carbure_client=self.entity,
            carbure_supplier=None,
            period=202201,
            year=2022,
            declared_by_supplier=True,
            declared_by_client=False,
        )

    def get_entity_lots(self, **kwargs):
        sent_lots = CarbureLot.objects.filter(carbure_supplier=self.entity, **kwargs)
        received_lots = CarbureLot.objects.filter(carbure_client=self.entity, **kwargs)
        return sent_lots, received_lots

    def test_validate_declaration(self):
        query = {
            "entity_id": self.entity.id,
            "period": 202201,
        }

        response = self.client.post(reverse("api-v5-declaration-validate"), query)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")

        sent_lots, received_lots = self.get_entity_lots()

        declared_sent_lots = sent_lots.filter(
            lot_status=CarbureLot.FROZEN,
            declared_by_supplier=True,
            declared_by_client=True,
        )

        self.assertEqual(declared_sent_lots.count(), 50)

        declared_received_lots = received_lots.filter(
            lot_status=CarbureLot.FROZEN,
            declared_by_supplier=True,
            declared_by_client=True,
        )

        self.assertEqual(declared_received_lots.count(), 50)

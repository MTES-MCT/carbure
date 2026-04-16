from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from core.carburetypes import CarbureError
from core.models import CarbureLot, Entity
from core.tests_utils import setup_current_user
from transactions.factories import CarbureLotFactory
from transactions.models import YearConfig


class ValidateDeclarationTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/entities_sites.json",
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
            delivery_type=CarbureLot.DIRECT,
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
            delivery_type=CarbureLot.DIRECT,
        )

    def get_entity_lots(self, **kwargs):
        sent_lots = CarbureLot.objects.filter(carbure_supplier=self.entity, **kwargs)
        received_lots = CarbureLot.objects.filter(carbure_client=self.entity, **kwargs)
        return sent_lots, received_lots

    def test_validate_declaration(self):
        YearConfig.objects.create(year=2021, locked=True)

        query = {
            "entity_id": self.entity.id,
            "period": 202201,
        }

        response = self.client.post(reverse("transactions-declarations-validate"), query)

        assert response.status_code == 200
        assert response.json()["status"] == "success"

        sent_lots, received_lots = self.get_entity_lots()

        declared_sent_lots = sent_lots.filter(
            lot_status=CarbureLot.FROZEN,
            declared_by_supplier=True,
            declared_by_client=True,
        )

        assert declared_sent_lots.count() == 50

        declared_received_lots = received_lots.filter(
            lot_status=CarbureLot.FROZEN,
            declared_by_supplier=True,
            declared_by_client=True,
        )

        assert declared_received_lots.count() == 50

    def test_validate_declaration_on_locked_year(self):
        YearConfig.objects.create(year=2022, locked=True)

        query = {
            "entity_id": self.entity.id,
            "period": 202201,
        }

        response = self.client.post(reverse("transactions-declarations-validate"), query)

        assert response.status_code == 400
        assert response.json()["status"] == "error"
        assert response.json()["error"] == CarbureError.YEAR_LOCKED


class ValidateDeclarationMacLotsTest(TestCase):
    """Tests for the mac_lots inclusion in validate_declaration."""

    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
    ]

    def setUp(self):
        self.supplier_with_mac = Entity.objects.filter(entity_type=Entity.TRADER, has_mac=True).first()
        self.client_entity = Entity.objects.filter(entity_type=Entity.OPERATOR).first()
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.supplier_with_mac, "ADMIN")])

        # Create RFC lots sent by supplier with has_mac=True (mac_lots candidates)
        CarbureLotFactory.create_batch(
            5,
            lot_status=CarbureLot.ACCEPTED,
            correction_status=CarbureLot.NO_PROBLEMO,
            carbure_supplier=self.supplier_with_mac,
            carbure_client=self.client_entity,
            period=202201,
            year=2022,
            declared_by_supplier=False,
            declared_by_client=True,
            delivery_type=CarbureLot.RFC,
        )

        # Create non-RFC lots sent by supplier with has_mac=True (should NOT be mac_lots)
        CarbureLotFactory.create_batch(
            3,
            lot_status=CarbureLot.ACCEPTED,
            correction_status=CarbureLot.NO_PROBLEMO,
            carbure_supplier=self.supplier_with_mac,
            carbure_client=self.client_entity,
            period=202201,
            year=2022,
            declared_by_supplier=False,
            declared_by_client=True,
            delivery_type=CarbureLot.DIRECT,
        )

    @patch("transactions.api.declarations.validate.background_create_tiruert_operations_from_lots")
    def test_mac_lots_included_when_supplier_has_mac(self, mock_tiruert):
        """RFC lots from a supplier with has_mac=True must be included in TIRUERT lots."""
        YearConfig.objects.create(year=2021, locked=True)

        query = {"entity_id": self.supplier_with_mac.id, "period": 202201}
        response = self.client.post(reverse("transactions-declarations-validate"), query)

        assert response.status_code == 200

        # background_create_tiruert_operations_from_lots must have been called once
        mock_tiruert.assert_called_once()

        tiruert_lots_qs = mock_tiruert.call_args[0][0]
        tiruert_lot_ids = set(tiruert_lots_qs.values_list("id", flat=True))

        # RFC lots from supplier with has_mac should be in tiruert_lots
        mac_lots = CarbureLot.objects.filter(carbure_supplier=self.supplier_with_mac, delivery_type=CarbureLot.RFC)
        for lot in mac_lots:
            self.assertIn(
                lot.id, tiruert_lot_ids, f"RFC lot {lot.id} sent by a supplier with has_mac should be in tiruert_lots"
            )

    @patch("transactions.api.declarations.validate.background_create_tiruert_operations_from_lots")
    def test_non_rfc_lots_not_included_as_mac_lots(self, mock_tiruert):
        """Non-RFC lots are not included as mac_lots, even if supplier has has_mac=True."""
        YearConfig.objects.create(year=2021, locked=True)

        query = {"entity_id": self.supplier_with_mac.id, "period": 202201}
        response = self.client.post(reverse("transactions-declarations-validate"), query)

        assert response.status_code == 200

        mock_tiruert.assert_called_once()
        tiruert_lots_qs = mock_tiruert.call_args[0][0]
        tiruert_lot_ids = set(tiruert_lots_qs.values_list("id", flat=True))

        # Non-RFC lots from supplier (DIRECT) should not appear as extra "mac_lots"
        # (they could appear as received lots but here carbure_client != supplier, so they won't)
        direct_sent_lots = CarbureLot.objects.filter(
            carbure_supplier=self.supplier_with_mac, delivery_type=CarbureLot.DIRECT
        )
        for lot in direct_sent_lots:
            self.assertNotIn(
                lot.id,
                tiruert_lot_ids,
                f"DIRECT lot {lot.id} should not be included as mac_lot",
            )

    @patch("transactions.api.declarations.validate.background_create_tiruert_operations_from_lots")
    def test_mac_lots_not_included_when_supplier_has_no_mac(self, mock_tiruert):
        """RFC lots from a supplier without has_mac=False must not be included as mac_lots."""
        YearConfig.objects.create(year=2021, locked=True)

        # Create a supplier without has_mac and RFC lots
        supplier_no_mac = Entity.objects.create(
            name="Supplier Without MAC",
            entity_type=Entity.OPERATOR,
            has_mac=False,
        )
        setup_current_user(self, "tester2@carbure.local", "Tester2", "gogogo2", [(supplier_no_mac, "ADMIN")])

        CarbureLotFactory.create_batch(
            3,
            lot_status=CarbureLot.ACCEPTED,
            correction_status=CarbureLot.NO_PROBLEMO,
            carbure_supplier=supplier_no_mac,
            carbure_client=self.client_entity,
            period=202201,
            year=2022,
            declared_by_supplier=False,
            declared_by_client=True,
            delivery_type=CarbureLot.RFC,
        )

        query = {"entity_id": supplier_no_mac.id, "period": 202201}
        response = self.client.post(reverse("transactions-declarations-validate"), query)

        assert response.status_code == 200

        mock_tiruert.assert_called_once()
        tiruert_lots_qs = mock_tiruert.call_args[0][0]
        tiruert_lot_ids = set(tiruert_lots_qs.values_list("id", flat=True))

        rfc_lots_no_mac = CarbureLot.objects.filter(carbure_supplier=supplier_no_mac, delivery_type=CarbureLot.RFC)
        for lot in rfc_lots_no_mac:
            self.assertNotIn(
                lot.id,
                tiruert_lot_ids,
                f"RFC lot {lot.id} from supplier without has_mac should not be a mac_lot",
            )

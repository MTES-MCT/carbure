from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from core.models import CarbureLot, Entity, UserRights
from core.tests_utils import setup_current_user
from transactions.factories.carbure_lot import CarbureLotFactory


class AdminUpdateManyCorrectionTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/entities_sites.json",
    ]

    def setUp(self):
        self.admin = Entity.objects.filter(entity_type=Entity.ADMIN)[0]
        self.user = setup_current_user(
            self,
            "admin@carbure.local",
            "Admin Tester",
            "gogogo",
            [(self.admin, UserRights.ADMIN)],
            is_staff=True,
        )

        self.lot = CarbureLotFactory.create(
            lot_status=CarbureLot.PENDING,
            correction_status=CarbureLot.NO_PROBLEMO,
            eec=10,
            el=0,
            ep=5,
            etd=5,
            eu=0,
            esca=0,
            eccs=0,
            eccr=0,
            eee=0,
            parent_lot=None,
            parent_stock=None,
        )
        self.lot.update_ghg()
        self.lot.save()

    def post_update_many(self, **payload):
        return self.client.post(
            reverse("transactions-admin-lots-update-many"),
            {
                "entity_id": self.admin.id,
                "lots_ids": [self.lot.id],
                "comment": "admin update",
                **payload,
            },
        )

    @patch("transactions.api.admin.lots.update_many.CorrectionService.create_correction_operations_for_lot_ghg_update")
    def test_update_many_triggers_sync_correction_service_on_ghg_change(self, correction_mock):
        """Admin bulk update must synchronously trigger correction creation for lots whose ghg_total changed."""
        response = self.post_update_many(eec=self.lot.eec + 12)

        assert response.status_code == 200, response.json()
        correction_mock.assert_called_once_with([self.lot.id])

        self.lot.refresh_from_db()
        assert self.lot.eec == 22

    @patch("transactions.api.admin.lots.update_many.CorrectionService.create_correction_operations_for_lot_ghg_update")
    def test_update_many_skips_correction_when_ghg_is_unchanged(self, correction_mock):
        """No correction must be created when the admin update does not change ghg_total."""
        response = self.post_update_many(free_field="some admin note")

        assert response.status_code == 200, response.json()
        correction_mock.assert_not_called()

    @patch("transactions.api.admin.lots.update_many.CorrectionService.create_correction_operations_for_lot_ghg_update")
    def test_update_many_skips_correction_on_dry_run(self, correction_mock):
        """Dry runs must not persist anything, including correction operations."""
        response = self.post_update_many(eec=self.lot.eec + 12, dry_run=True)

        assert response.status_code == 200, response.json()
        correction_mock.assert_not_called()

        self.lot.refresh_from_db()
        assert self.lot.eec == 10

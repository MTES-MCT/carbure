from datetime import date
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from core.models import Biocarburant, CarbureLot, Entity, GenericError, MatierePremiere, UserRights
from core.tests_utils import setup_current_user
from tiruert.models import Operation
from tiruert.services.correction import CorrectionService
from tiruert.services.operation import OperationService
from transactions.factories.carbure_lot import CarbureLotFactory
from transactions.factories.certificate import GenericCertificateFactory
from transactions.models import Depot


class AdminUpdateManyCorrectionTestBase(TestCase):
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
        self.operator = Entity.objects.filter(entity_type=Entity.OPERATOR)[0]
        self.user = setup_current_user(
            self,
            "admin@carbure.local",
            "Admin Tester",
            "gogogo",
            [(self.admin, UserRights.ADMIN)],
            is_staff=True,
        )

        GenericCertificateFactory.create(
            certificate_id="VALID",
            valid_from=date(2000, 1, 1),
            valid_until=date(3000, 1, 1),
        )
        self.lot = CarbureLotFactory.create(
            lot_status=CarbureLot.ACCEPTED,
            correction_status=CarbureLot.NO_PROBLEMO,
            delivery_type=CarbureLot.BLENDING,
            carbure_client=self.operator,
            added_by=self.operator,
            carbure_delivery_site=Depot.objects.first(),
            feedstock=MatierePremiere.biofuel.filter(category="CONV").first(),
            biofuel=Biocarburant.objects.get(code="ETH"),
            supplier_certificate="VALID",
            volume=1000,
            eec=10,
            ep=5,
            etd=5,
            el=0,
            eu=0,
            esca=0,
            eccs=0,
            eccr=0,
            eee=0,
            ghg_total=20,
            parent_lot=None,
            parent_stock=None,
        )

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


class AdminUpdateManyVolumeCorrectionTest(AdminUpdateManyCorrectionTestBase):
    def setUp(self):
        super().setUp()
        OperationService.create_operations_from_lots(CarbureLot.objects.filter(id=self.lot.id))

    @patch(
        "transactions.api.admin.lots.update_many.CorrectionService.create_correction_operations_for_lot_update",
        side_effect=CorrectionService.create_correction_operations_for_lot_volume_update,
        create=True,
    )
    def test_update_many_creates_correction_when_volume_changes(self, correction_mock):
        """Create a volume correction after an admin changes a lot's volume."""
        response = self.post_update_many(volume=1200)

        assert response.status_code == 200, response.json()
        correction_mock.assert_called_once_with([self.lot.id])
        correction = Operation.objects.get(type=Operation.CORRECTION)
        assert correction.credited_entity == self.operator
        assert correction.details.get().volume == 199  # 200 L converted to ethanol 15°

    def test_update_many_skips_correction_when_volume_is_unchanged(self):
        """Do not create a correction when an admin update leaves the volume unchanged."""
        response = self.post_update_many(eec=10)

        assert response.status_code == 200, response.json()
        assert not Operation.objects.filter(type=Operation.CORRECTION).exists()

    def test_update_many_skips_correction_on_dry_run(self):
        """Do not persist a volume correction during an admin dry run."""
        response = self.post_update_many(volume=1200, dry_run=True)

        assert response.status_code == 200, response.json()
        assert not Operation.objects.filter(type=Operation.CORRECTION).exists()


class AdminUpdateManyCorrectionTriggerTest(AdminUpdateManyCorrectionTestBase):
    def setUp(self):
        super().setUp()
        correction_patch = patch(
            "transactions.api.admin.lots.update_many.CorrectionService.create_correction_operations_for_lot_update",
            create=True,
        )
        self.correction_mock = correction_patch.start()
        self.addCleanup(correction_patch.stop)

    def test_update_many_triggers_common_correction_when_volume_changes(self):
        """Send a validated admin volume change to the common correction service."""
        response = self.post_update_many(volume=1200)

        assert response.status_code == 200, response.json()
        self.lot.refresh_from_db()
        assert self.lot.volume == 1200
        self.correction_mock.assert_called_once_with([self.lot.id])

    def test_update_many_triggers_common_correction_when_ghg_changes(self):
        """Detect the GHG change independently of the mutable event diff."""
        response = self.post_update_many(eec=11)

        assert response.status_code == 200, response.json()
        self.lot.refresh_from_db()
        assert self.lot.ghg_total == 21
        assert self.lot.volume == 1000
        self.correction_mock.assert_called_once_with([self.lot.id])

    def test_update_many_triggers_one_common_correction_for_volume_and_ghg(self):
        """Apply combined admin volume and GHG changes through one service call."""
        response = self.post_update_many(volume=1200, eec=11)

        assert response.status_code == 200, response.json()
        self.lot.refresh_from_db()
        assert self.lot.volume == 1200
        assert self.lot.ghg_total == 21
        self.correction_mock.assert_called_once_with([self.lot.id])

    def test_update_many_skips_common_correction_when_ghg_total_is_unchanged(self):
        """Ignore changed GHG components when they leave the total unchanged."""
        response = self.post_update_many(eec=11, ep=4)

        assert response.status_code == 200, response.json()
        self.lot.refresh_from_db()
        assert self.lot.ghg_total == 20
        self.correction_mock.assert_not_called()

    def test_update_many_never_triggers_common_correction_on_dry_run(self):
        """Keep volume and GHG previews free of correction side effects."""
        for update in ({"volume": 1200}, {"eec": 11}, {"volume": 1200, "eec": 11}):
            with self.subTest(update=update):
                response = self.post_update_many(**update, dry_run=True)

                assert response.status_code == 200, response.json()
                self.lot.refresh_from_db()
                assert self.lot.volume == 1000
                assert self.lot.ghg_total == 20
                self.correction_mock.assert_not_called()

    @patch("transactions.api.admin.lots.update_many.bulk_sanity_checks")
    def test_update_many_does_not_trigger_common_correction_before_validation(self, sanity_checks_mock):
        """Do not persist or correct an admin update rejected by blocking checks."""
        sanity_checks_mock.return_value = [GenericError(lot=self.lot, field="eec", error="BLOCKING_ERROR", is_blocking=True)]

        response = self.post_update_many(eec=11)

        assert response.status_code == 400, response.json()
        assert response.json()["error"] == "SANITY_CHECKS_FAILED"
        self.lot.refresh_from_db()
        assert self.lot.ghg_total == 20
        self.correction_mock.assert_not_called()

    def test_update_many_includes_ghg_descendants(self):
        """Apply an admin GHG update to every changed lot in the propagation chain."""
        child = CarbureLotFactory.create(
            parent_lot=self.lot,
            lot_status=CarbureLot.ACCEPTED,
            correction_status=CarbureLot.NO_PROBLEMO,
            added_by=self.operator,
            carbure_supplier=self.operator,
            carbure_client=self.operator,
            biofuel=self.lot.biofuel,
            feedstock=self.lot.feedstock,
            volume=self.lot.volume,
            eec=10,
            ep=5,
            etd=5,
            el=0,
            eu=0,
            esca=0,
            eccs=0,
            eccr=0,
            eee=0,
            ghg_total=20,
            supplier_certificate="VALID",
        )

        response = self.post_update_many(eec=11)

        assert response.status_code == 200, response.json()
        child.refresh_from_db()
        assert child.ghg_total == 21
        self.correction_mock.assert_called_once_with(sorted([self.lot.id, child.id]))

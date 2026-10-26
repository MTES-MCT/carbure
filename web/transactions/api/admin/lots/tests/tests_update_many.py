from datetime import date

from django.test import TestCase
from django.urls import reverse

from core.models import Biocarburant, CarbureLot, Entity, MatierePremiere, UserRights
from core.tests_utils import setup_current_user
from tiruert.models import Operation
from tiruert.services.operation import OperationService
from transactions.factories.carbure_lot import CarbureLotFactory
from transactions.factories.certificate import GenericCertificateFactory
from transactions.models import Depot


class AdminUpdateManyVolumeCorrectionTest(TestCase):
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
            parent_lot=None,
            parent_stock=None,
        )
        OperationService.create_operations_from_lots(CarbureLot.objects.filter(id=self.lot.id))

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

    def test_update_many_creates_correction_when_volume_changes(self):
        """Create a volume correction after an admin changes a lot's volume."""
        response = self.post_update_many(volume=1200)

        assert response.status_code == 200, response.json()
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

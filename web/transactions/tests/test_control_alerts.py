from django.test import TestCase
from django.urls import reverse

from core.models import CarbureLot, Entity, UserRights
from core.tests_utils import setup_current_user
from entity.factories.entity import EntityFactory
from transactions.repositories.admin_lots_repository import TransactionsAdminLotsRepository
from transactions.repositories.audit_lots_repository import TransactionsAuditLotsRepository


class ControlAlertsTest(TestCase):
    def setUp(self):
        self.producer = EntityFactory.create(entity_type=Entity.PRODUCER)
        self.admin = EntityFactory.create(entity_type=Entity.ADMIN)
        self.auditor = EntityFactory.create(entity_type=Entity.AUDITOR)
        setup_current_user(
            self,
            "controls@carbure.local",
            "Controller",
            "password",
            [(self.admin, UserRights.RW), (self.auditor, UserRights.RW), (self.producer, UserRights.AUDITOR)],
            is_staff=True,
        )
        self.manual_admin = self.create_lot(highlighted_by_admin=True)
        self.manual_auditor = self.create_lot(highlighted_by_auditor=True)
        self.random = self.create_lot(random_control_requested=True)
        self.create_lot()
        self.create_lot(random_control_requested=True, audit_status=CarbureLot.CONFORM)
        self.create_lot(random_control_requested=True, lot_status=CarbureLot.DRAFT)
        self.create_lot(random_control_requested=True, lot_status=CarbureLot.DELETED)

    def create_lot(self, **kwargs):
        defaults = {
            "year": 2026,
            "period": 202601,
            "lot_status": CarbureLot.ACCEPTED,
            "carbure_supplier": self.producer,
        }
        return CarbureLot.objects.create(**(defaults | kwargs))

    def test_admin_alert_list_and_snapshot_keep_manual_and_random_controls(self):
        response = self.client.get(
            reverse("transactions-admin-controls-snapshot"), {"entity_id": self.admin.pk, "year": 2026}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["lots"]["alerts"], 2)
        lots = TransactionsAdminLotsRepository.get_admin_lots_by_status(self.admin, "ALERTS")
        self.assertCountEqual(lots.values_list("pk", flat=True), [self.manual_admin.pk, self.random.pk])

    def test_auditor_alert_list_and_snapshot_keep_manual_and_random_controls(self):
        response = self.client.get(reverse("transactions-audit-snapshot"), {"entity_id": self.auditor.pk, "year": 2026})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["lots"]["alerts"], 2)
        lots = TransactionsAuditLotsRepository.get_auditor_lots_by_status(self.auditor, "ALERTS", response.wsgi_request)
        self.assertCountEqual(lots.values_list("pk", flat=True), [self.manual_auditor.pk, self.random.pk])

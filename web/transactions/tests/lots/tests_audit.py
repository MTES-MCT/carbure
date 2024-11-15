from django.urls import reverse

from core.models import CarbureLot, Entity, UserRights
from transactions.tests.lots import TestCase


class LotsAuditTest(TestCase):
    def setUp(self):
        super().setUp()
        self.auditor = Entity.objects.filter(entity_type=Entity.AUDITOR).first()
        UserRights.objects.update_or_create(entity=self.auditor, user=self.user1, role=UserRights.RW)

    def test_mark_conform(self):
        lot = self.create_draft()
        response = self.client.post(
            reverse("transactions-lots-mark-conform") + f"?entity_id={self.auditor.id}",
            {"selection": [lot.id]},
        )
        assert response.status_code == 200
        lot.refresh_from_db()
        assert lot.audit_status == CarbureLot.CONFORM

    def test_mark_non_conform(self):
        lot = self.create_draft()
        response = self.client.post(
            reverse("transactions-lots-mark-non-conform") + f"?entity_id={self.auditor.id}",
            {"selection": [lot.id]},
        )
        assert response.status_code == 200
        lot.refresh_from_db()
        assert lot.audit_status == CarbureLot.NONCONFORM

    def test_toggle_pin_audit(self):
        lot = self.create_draft()
        response = self.client.post(
            reverse("transactions-lots-toggle-pin") + f"?entity_id={self.auditor.id}",
            {"selection": [lot.id], "notify_admin": True},
        )
        assert response.status_code == 200
        lot.refresh_from_db()
        assert lot.highlighted_by_admin is True

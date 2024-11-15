from django.urls import reverse

from core.models import Entity, UserRights
from transactions.models import YearConfig
from transactions.tests.lots import TestCase


class LotsAdminTest(TestCase):
    def setUp(self):
        super().setUp()
        self.admin = Entity.objects.filter(entity_type=Entity.ADMIN).first()
        UserRights.objects.update_or_create(entity=self.admin, user=self.user1, role=UserRights.ADMIN)

    def test_toggle_pin_admin(self):
        lot = self.create_draft()
        response = self.client.post(
            reverse("v2-transactions-lots-toggle-pin") + f"?entity_id={self.admin.id}",
            {"selection": [lot.id], "notify_auditor": True},
        )
        assert response.status_code == 200
        lot.refresh_from_db()
        assert lot.highlighted_by_auditor is True

    def test_delete_many(self):
        lot = self.create_draft()
        response = self.client.post(
            reverse("v2-transactions-lots-delete-many") + f"?entity_id={self.admin.id}",
            {"lots_ids": [lot.id], "dry_run": True, "comment": "hi"},
        )
        data = response.json()
        assert response.status_code == 200
        assert data["deletions"][0]["node"]["id"] == lot.id

    def test_update_many(self):
        YearConfig.objects.create(year=2018, locked=True)
        lot = self.create_draft()

        data = {
            "lots_ids": [lot.id],
            "dry_run": True,
            "comment": "hi",
            "transport_document_reference": "DAETEST_UPDATE",
        }
        response = self.client.post(
            reverse("v2-transactions-lots-update-many") + f"?entity_id={self.admin.id}",
            data,
        )
        data = response.json()
        assert data["updates"][0]["node"]["id"] == lot.id
        assert data["updates"][0]["diff"]["changed"][0] == ["transport_document_reference", "DAETEST", "DAETEST_UPDATE"]
        assert response.status_code == 200

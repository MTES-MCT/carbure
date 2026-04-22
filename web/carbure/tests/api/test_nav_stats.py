from django.test import TestCase
from django.urls import reverse

from core.models import Entity, UserRights
from core.tests_utils import setup_current_user


class NavStatsAuthAndPermissionsTest(TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("carbure-nav-stats")
        self.entity = Entity.objects.create(
            name="Entity nav stats",
            entity_type=Entity.OPERATOR,
            has_elec=False,
            is_tiruert_liable=False,
            accise_number="ACC123",
        )
        self.other_entity = Entity.objects.create(
            name="Other entity nav stats",
            entity_type=Entity.OPERATOR,
            has_elec=False,
            is_tiruert_liable=False,
            accise_number="ACC456",
        )

    def test_nav_stats_requires_authentication(self):
        response = self.client.get(self.url, {"entity_id": self.entity.id})

        self.assertEqual(response.status_code, 403)

    def test_nav_stats_requires_user_rights_on_entity(self):
        setup_current_user(
            self,
            "no-rights@carbure.local",
            "No Rights",
            "secret",
            [(self.other_entity, UserRights.ADMIN)],
        )

        response = self.client.get(self.url, {"entity_id": self.entity.id})

        self.assertEqual(response.status_code, 403)

    def test_nav_stats_returns_data_for_user_with_rights(self):
        setup_current_user(
            self,
            "with-rights@carbure.local",
            "With Rights",
            "secret",
            [(self.entity, UserRights.ADMIN)],
        )

        response = self.client.get(self.url, {"entity_id": self.entity.id})

        self.assertEqual(response.status_code, 200)
        self.assertIn("pending_draft_lots", response.json())

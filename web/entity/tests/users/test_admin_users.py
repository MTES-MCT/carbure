from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.models import Entity, UserRights, UserRightsRequests
from core.tests_utils import FiltersActionTestMixin, setup_current_user
from entity.views.users.admin_users import AdminUsersViewSet

User = get_user_model()


def row_by_email(results, email, entity_name):
    matches = [row for row in results if row["email"] == email and row["entity_name"] == entity_name]
    assert len(matches) == 1, matches
    return matches[0]


class AdminUsersTest(FiltersActionTestMixin, TestCase):
    def setUp(self):
        self.admin = Entity.objects.create(name="Admin Carbure", entity_type=Entity.ADMIN)
        self.producer = Entity.objects.create(name="Producteur Alpha", entity_type=Entity.PRODUCER)
        self.operator = Entity.objects.create(name="Operateur Beta", entity_type=Entity.OPERATOR)
        self.user = setup_current_user(
            self,
            "admin@carbure.local",
            "Admin",
            "gogogo",
            [(self.admin, UserRights.ADMIN)],
            is_staff=True,
        )
        self.list_url = reverse("api-entity-admin-users-list")
        self.search_url = reverse("api-entity-admin-users-search")

    def results(self, **params):
        response = self.client.get(self.list_url, {"entity_id": self.admin.id, **params})
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()["results"]

    def test_forbidden_for_non_admin_entity(self):
        producer_user = setup_current_user(
            self,
            "producer@carbure.local",
            "Producer",
            "gogogo",
            [(self.producer, UserRights.ADMIN)],
            is_staff=True,
        )
        self.client.force_login(producer_user)
        response = self.client.get(self.list_url, {"entity_id": self.producer.id})
        self.assertEqual(response.status_code, 403)

    def test_lists_only_granted_rights(self):
        accepted = User.objects.create_user(email="accepted@carbure.local", name="Accepté", password="x", is_active=True)
        UserRightsRequests.objects.create(user=accepted, entity=self.producer, status="ACCEPTED", role=UserRights.RO)
        UserRights.objects.create(user=accepted, entity=self.producer, role=UserRights.ADMIN)

        pending = User.objects.create_user(email="pending@carbure.local", name="Attente", password="x")
        UserRightsRequests.objects.create(user=pending, entity=self.producer, status="PENDING", role=UserRights.RW)

        User.objects.create_user(email="alone@carbure.local", name="Seul", password="x")

        staff = User.objects.create_user(email="staff@carbure.local", name="Staff", password="x", is_staff=True)
        UserRights.objects.create(user=staff, entity=self.producer, role=UserRights.ADMIN)

        multi = User.objects.create_user(email="multi@carbure.local", name="Multi", password="x")
        UserRights.objects.create(user=multi, entity=self.producer, role=UserRights.RO)
        UserRights.objects.create(user=multi, entity=self.operator, role=UserRights.RW)

        rows = self.results()
        emails = {row["email"] for row in rows}
        self.assertNotIn("pending@carbure.local", emails)
        self.assertNotIn("alone@carbure.local", emails)
        self.assertNotIn("staff@carbure.local", emails)
        self.assertNotIn(self.user.email, emails)

        accepted_row = row_by_email(rows, "accepted@carbure.local", "Producteur Alpha")
        self.assertEqual(accepted_row["role"], UserRights.ADMIN)
        self.assertEqual(accepted_row["entity_type"], Entity.PRODUCER)
        self.assertTrue(accepted_row["is_active"])
        self.assertEqual(row_by_email(rows, "multi@carbure.local", "Producteur Alpha")["role"], UserRights.RO)
        self.assertEqual(row_by_email(rows, "multi@carbure.local", "Operateur Beta")["role"], UserRights.RW)

    def test_closed_entity_stays_visible(self):
        closed = Entity.objects.create(name="Entité close", entity_type=Entity.TRADER)
        user = User.objects.create_user(email="closed@carbure.local", name="Clos", password="x")
        UserRights.objects.create(user=user, entity=closed, role=UserRights.RO)
        Entity.all_objects.filter(pk=closed.pk).update(closed_at=timezone.now())

        row = row_by_email(self.results(search="closed@"), "closed@carbure.local", "Entité close")
        self.assertEqual(row["entity_type"], Entity.TRADER)
        self.assertEqual(row["role"], UserRights.RO)

    def test_filters_and_search(self):
        user = User.objects.create_user(email="filtre@carbure.local", name="Filtre", password="x")
        UserRights.objects.create(user=user, entity=self.producer, role=UserRights.RW)
        other = User.objects.create_user(email="autre@carbure.local", name="Autre", password="x", is_active=False)
        UserRights.objects.create(user=other, entity=self.operator, role=UserRights.RO)

        by_email = self.results(search="filtre@")
        self.assertEqual([row["email"] for row in by_email], ["filtre@carbure.local"])

        by_entity = self.results(search="Alpha")
        self.assertTrue(any(row["email"] == "filtre@carbure.local" for row in by_entity))
        self.assertFalse(any(row["email"] == "autre@carbure.local" for row in by_entity))

        by_type = self.results(entity_type=Entity.OPERATOR)
        self.assertTrue(all(row["entity_type"] == Entity.OPERATOR for row in by_type))

        by_role = self.results(role=UserRights.RW)
        self.assertTrue(all(row["role"] == UserRights.RW for row in by_role))

        active_rows = self.results(is_active="true")
        self.assertEqual([row["email"] for row in active_rows], ["filtre@carbure.local"])

        inactive_rows = self.results(is_active="false")
        self.assertEqual([row["email"] for row in inactive_rows], ["autre@carbure.local"])

        self.assertEqual(self.results(search=f"{self.producer.id}, {self.operator.id}"), [])

        by_entity_ids = self.post_results(f"{self.producer.id}, {self.operator.id}")
        self.assertEqual(
            sorted(row["email"] for row in by_entity_ids),
            ["autre@carbure.local", "filtre@carbure.local"],
        )

        by_lines = self.post_results(f"{self.producer.id}\n{self.operator.id}")
        self.assertEqual(
            sorted(row["email"] for row in by_lines),
            ["autre@carbure.local", "filtre@carbure.local"],
        )

    def test_filter_options(self):
        active = User.objects.create_user(email="actif@carbure.local", name="Actif", password="x")
        UserRights.objects.create(user=active, entity=self.producer, role=UserRights.RW)
        inactive = User.objects.create_user(email="inactif@carbure.local", name="Inactif", password="x", is_active=False)
        UserRights.objects.create(user=inactive, entity=self.operator, role=UserRights.RO)

        self.assertFilters(
            AdminUsersViewSet,
            {
                "entity_type": [Entity.OPERATOR, Entity.PRODUCER],
                "is_active": [False, True],
                "role": [UserRights.RO, UserRights.RW],
            },
        )

    def post_results(self, entity_ids, **params):
        response = self.client.post(
            self.search_url,
            {"entity_ids": entity_ids},
            query_params={"entity_id": self.admin.id, **params},
        )
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()["results"]

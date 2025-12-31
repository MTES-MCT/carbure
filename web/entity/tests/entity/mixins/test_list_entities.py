from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import Entity, ExternalAdminRights, UserRights, UserRightsRequests
from core.tests_utils import assert_object_contains_data, setup_current_user
from entity.factories.entity import EntityFactory


# Helper function to assert that the expected entities are in the entities_data
def expect_entities(test, expected_entities, entities_data):
    test.assertEqual(len(expected_entities), len(entities_data))
    for idx, expected_entity in enumerate(expected_entities):
        assert_object_contains_data(test, expected_entity.natural_key(), entities_data[idx]["entity"])


class EntityListActionTest(TestCase):
    """Tests to cover all branches of the list function"""

    def setUp(self):
        User = get_user_model()
        # Create different entities to test filters
        self.admin = EntityFactory.create(name="Admin Entity", entity_type=Entity.ADMIN)
        self.airline1 = EntityFactory.create(name="Airline 1", entity_type=Entity.AIRLINE)
        self.airline2 = EntityFactory.create(name="Airline 2", entity_type=Entity.AIRLINE)
        self.cpo1 = EntityFactory.create(name="CPO 1", entity_type=Entity.CPO)
        self.cpo2 = EntityFactory.create(name="CPO 2", entity_type=Entity.CPO)
        self.operator_elec = EntityFactory.create(name="Operator Elec", entity_type=Entity.OPERATOR, has_elec=True)
        self.operator_no_elec = EntityFactory.create(name="Operator No Elec", entity_type=Entity.OPERATOR, has_elec=False)
        self.producer1 = EntityFactory.create(name="Producer 1", entity_type=Entity.PRODUCER)
        self.producer2 = EntityFactory.create(name="Producer 2", entity_type=Entity.PRODUCER)
        self.trader = EntityFactory.create(name="Trader", entity_type=Entity.TRADER)

        # Create external admin entities with different rights
        self.ext_admin_airline = EntityFactory.create(name="Ext Admin Airline", entity_type=Entity.EXTERNAL_ADMIN)
        ExternalAdminRights.objects.create(entity=self.ext_admin_airline, right=ExternalAdminRights.AIRLINE)

        self.ext_admin_elec = EntityFactory.create(name="Ext Admin Elec", entity_type=Entity.EXTERNAL_ADMIN)
        ExternalAdminRights.objects.create(entity=self.ext_admin_elec, right=ExternalAdminRights.ELEC)

        self.ext_admin_transferred_elec = EntityFactory.create(
            name="Ext Admin Transferred Elec", entity_type=Entity.EXTERNAL_ADMIN
        )
        ExternalAdminRights.objects.create(
            entity=self.ext_admin_transferred_elec, right=ExternalAdminRights.TRANSFERRED_ELEC
        )

        self.ext_admin_double_counting = EntityFactory.create(
            name="Ext Admin Double Counting", entity_type=Entity.EXTERNAL_ADMIN
        )
        ExternalAdminRights.objects.create(entity=self.ext_admin_double_counting, right=ExternalAdminRights.DOUBLE_COUNTING)

        # Create users to test counters
        self.user1 = User.objects.create_user(email="user1@test.com", name="User 1", password="test")
        self.user2 = User.objects.create_user(email="user2@test.com", name="User 2", password="test")
        self.user3 = User.objects.create_user(email="user3@test.com", name="User 3", password="test")

        # Create UserRightsRequests with PENDING status to test has_requests filter
        UserRightsRequests.objects.create(entity=self.producer1, user=self.user1, role=UserRights.RO, status="PENDING")
        UserRightsRequests.objects.create(entity=self.producer2, user=self.user2, role=UserRights.RW, status="ACCEPTED")

    def test_list_as_admin_returns_all_entities(self):
        """Test that admin sees all entities"""
        setup_current_user(self, "admin@test.com", "Admin", "test", [(self.admin, "RW")], True)
        response = self.client.get(reverse("entity-list") + f"?entity_id={self.admin.id}")

        self.assertEqual(response.status_code, 200)
        entities_data = response.json()

        # Should return all created entities
        self.assertEqual(len(entities_data), 14)

    def test_list_with_airline_right_filters_airlines_only(self):
        """Test that AIRLINE filter returns only airlines"""
        setup_current_user(self, "airline_admin@test.com", "Airline Admin", "test", [(self.ext_admin_airline, "RW")], True)
        response = self.client.get(reverse("entity-list") + f"?entity_id={self.ext_admin_airline.id}")

        entities_data = response.json()

        # Should return only airlines
        expect_entities(self, [self.airline1, self.airline2], entities_data)

    def test_list_with_elec_right_filters_cpo_and_operators_with_elec(self):
        """Test that ELEC filter returns CPO and OPERATOR with has_elec=True"""
        setup_current_user(self, "elec_admin@test.com", "Elec Admin", "test", [(self.ext_admin_elec, "RW")], True)
        response = self.client.get(reverse("entity-list") + f"?entity_id={self.ext_admin_elec.id}")

        entities_data = response.json()

        # Should return CPO and OPERATOR with has_elec=True
        expected_entities = [self.cpo1, self.cpo2, self.operator_elec]
        expect_entities(self, expected_entities, entities_data)

    def test_list_with_transferred_elec_right_filters_cpo_and_all_operators(self):
        """Test that TRANSFERRED_ELEC filter returns CPO and all OPERATORs"""
        setup_current_user(
            self,
            "transferred_elec_admin@test.com",
            "Transferred Elec Admin",
            "test",
            [(self.ext_admin_transferred_elec, "RW")],
            True,
        )
        response = self.client.get(reverse("entity-list") + f"?entity_id={self.ext_admin_transferred_elec.id}")

        entities_data = response.json()
        # Should return CPO and all OPERATORs (with or without elec)
        expected_entities = [self.cpo1, self.cpo2, self.operator_elec, self.operator_no_elec]
        expect_entities(self, expected_entities, entities_data)

    def test_list_with_double_counting_right_filters_producers_only(self):
        """Test that DOUBLE_COUNTING filter returns only producers"""
        setup_current_user(
            self,
            "dc_admin@test.com",
            "Double Counting Admin",
            "test",
            [(self.ext_admin_double_counting, "RW")],
            True,
        )
        response = self.client.get(reverse("entity-list") + f"?entity_id={self.ext_admin_double_counting.id}")

        entities_data = response.json()

        # Should return only producers
        expected_entities = [self.producer1, self.producer2]
        expect_entities(self, expected_entities, entities_data)

    def test_list_with_query_param_q_filters_by_name(self):
        """Test that q parameter filters by name"""
        setup_current_user(self, "admin@test.com", "Admin", "test", [(self.admin, "RW")], True)
        response = self.client.get(reverse("entity-list") + f"?entity_id={self.admin.id}&q=Airline")

        entities_data = response.json()

        # Should return only entities with "Airline" in the name
        expected_entities = [self.airline1, self.airline2, self.ext_admin_airline]
        expect_entities(self, expected_entities, entities_data)

    def test_list_with_has_requests_true_filters_entities_with_pending_requests(self):
        """Test that has_requests=true parameter filters entities with pending requests"""
        setup_current_user(self, "admin@test.com", "Admin", "test", [(self.admin, "RW")], True)
        response = self.client.get(reverse("entity-list") + f"?entity_id={self.admin.id}&has_requests=true")

        entities_data = response.json()

        expected_entities = [self.producer1]
        expect_entities(self, expected_entities, entities_data)

    # def test_list_as_admin_includes_elec_annotations(self):
    #     """Test that admin sees elec annotations (charge_points and meter_readings)"""
    #     setup_current_user(self, "admin@test.com", "Admin", "test", [(self.admin, "RW")], True)
    #     response = self.client.get(reverse("entity-list") + f"?entity_id={self.admin.id}")

    #     self.assertEqual(response.status_code, 200)
    #     entities_data = response.json()
    #     # All entities should have elec fields
    #     for entity_data in entities_data:
    #         self.assertIn("charge_points_accepted", entity_data)
    #         self.assertIn("charge_points_pending", entity_data)
    #         self.assertIn("meter_readings_accepted", entity_data)
    #         self.assertIn("meter_readings_pending", entity_data)

    # def test_list_as_ext_admin_elec_includes_elec_annotations(self):
    #     """Test that external ELEC admin sees elec annotations"""
    #     setup_current_user(self, "elec_admin@test.com", "Elec Admin", "test", [(self.ext_admin_elec, "RW")], True)
    #     response = self.client.get(reverse("entity-list") + f"?entity_id={self.ext_admin_elec.id}")

    #     self.assertEqual(response.status_code, 200)
    #     entities_data = response.json()
    #     # All entities should have elec fields
    #     for entity_data in entities_data:
    #         self.assertIn("charge_points_accepted", entity_data)
    #         self.assertIn("charge_points_pending", entity_data)
    #         self.assertIn("meter_readings_accepted", entity_data)
    #         self.assertIn("meter_readings_pending", entity_data)

    # def test_list_as_admin_includes_admin_only_annotations(self):
    #     """Test that only admin sees admin annotations (depots, production_sites, certificates, double_counting)"""
    #     setup_current_user(self, "admin@test.com", "Admin", "test", [(self.admin, "RW")], True)
    #     response = self.client.get(reverse("entity-list") + f"?entity_id={self.admin.id}")

    #     self.assertEqual(response.status_code, 200)
    #     entities_data = response.json()
    #     # All entities should have admin fields
    #     for entity_data in entities_data:
    #         self.assertIn("depots", entity_data)
    #         self.assertIn("production_sites", entity_data)
    #         self.assertIn("certificates", entity_data)
    #         self.assertIn("certificates_pending", entity_data)
    #         self.assertIn("double_counting", entity_data)
    #         self.assertIn("double_counting_requests", entity_data)

    # def test_list_as_ext_admin_does_not_include_admin_only_annotations(self):
    #     """Test that external admin does not see admin annotations"""
    #     setup_current_user(self, "airline_admin@test.com", "Airline Admin", "test", [(self.ext_admin_airline, "RW")], True)
    #     response = self.client.get(reverse("entity-list") + f"?entity_id={self.ext_admin_airline.id}")

    #     self.assertEqual(response.status_code, 200)
    #     entities_data = response.json()
    #     # Entities should not have admin fields (should be 0)
    #     for entity_data in entities_data:
    #         self.assertEqual(entity_data["depots"], 0)
    #         self.assertEqual(entity_data["production_sites"], 0)
    #         self.assertEqual(entity_data["certificates"], 0)
    #         self.assertEqual(entity_data["certificates_pending"], 0)
    #         self.assertEqual(entity_data["double_counting"], 0)
    #         self.assertEqual(entity_data["double_counting_requests"], 0)

    # def test_list_entities_sorted_by_name(self):
    #     """Test that entities are sorted by name"""
    #     setup_current_user(self, "admin@test.com", "Admin", "test", [(self.admin, "RW")], True)
    #     response = self.client.get(reverse("entity-list") + f"?entity_id={self.admin.id}")

    #     self.assertEqual(response.status_code, 200)
    #     entities_data = response.json()
    #     # Verify that entities are sorted by name
    #     names = [e["entity"]["name"] for e in entities_data]
    #     self.assertEqual(names, sorted(names))

    # def test_list_returns_all_required_fields(self):
    #     """Test that response contains all required fields"""
    #     setup_current_user(self, "admin@test.com", "Admin", "test", [(self.admin, "RW")], True)
    #     response = self.client.get(reverse("entity-list") + f"?entity_id={self.admin.id}")

    #     self.assertEqual(response.status_code, 200)
    #     entities_data = response.json()
    #     self.assertGreater(len(entities_data), 0)

    #     required_fields = [
    #         "entity",
    #         "users",
    #         "requests",
    #         "depots",
    #         "production_sites",
    #         "certificates",
    #         "double_counting",
    #         "double_counting_requests",
    #         "certificates_pending",
    #         "charge_points_accepted",
    #         "charge_points_pending",
    #         "meter_readings_accepted",
    #         "meter_readings_pending",
    #     ]

    #     for entity_data in entities_data:
    #         for field in required_fields:
    #             self.assertIn(field, entity_data, f"Field {field} is missing in response")

    # def test_list_with_multiple_filters_combined(self):
    #     """Test combination of multiple filters"""
    #     setup_current_user(self, "admin@test.com", "Admin", "test", [(self.admin, "RW")], True)
    #     # Filter by name and has_requests
    #     response = self.client.get(reverse("entity-list") + f"?entity_id={self.admin.id}&q=Producer&has_requests=true")

    #     self.assertEqual(response.status_code, 200)
    #     entities_data = response.json()
    #     # Should return only producers with pending requests
    #     for entity_data in entities_data:
    #         self.assertIn("Producer", entity_data["entity"]["name"])
    #         self.assertGreater(entity_data["requests"], 0)

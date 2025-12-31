from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import Entity, ExternalAdminRights, UserRights, UserRightsRequests
from core.tests_utils import assert_object_contains_data, setup_current_user
from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from entity.factories.entity import EntityFactory
from transactions.factories.certificate import EntityCertificateFactory, GenericCertificateFactory


# Helper function to assert that the expected entities are in the entities_data
def expect_entities(test, expected_entities, entities_data):
    test.assertEqual(len(expected_entities), len(entities_data))
    for idx, expected_entity in enumerate(expected_entities):
        assert_object_contains_data(test, expected_entity.natural_key(), entities_data[idx]["entity"])


# Helper function to get the CPO entity with applications and meter readings
def add_elec_applications_and_meter_readings_to_entity(entity):
    ElecChargePointApplication.objects.create(cpo=entity, status=ElecChargePointApplication.ACCEPTED)
    ElecChargePointApplication.objects.create(cpo=entity, status=ElecChargePointApplication.ACCEPTED)
    ElecChargePointApplication.objects.create(cpo=entity, status=ElecChargePointApplication.PENDING)
    ElecMeterReadingApplication.objects.create(cpo=entity, status=ElecMeterReadingApplication.ACCEPTED, quarter=1, year=2024)
    ElecMeterReadingApplication.objects.create(cpo=entity, status=ElecMeterReadingApplication.PENDING, quarter=2, year=2024)
    ElecMeterReadingApplication.objects.create(cpo=entity, status=ElecMeterReadingApplication.PENDING, quarter=3, year=2024)


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

        # Create ElecChargePointApplications to test elec annotations
        add_elec_applications_and_meter_readings_to_entity(self.cpo1)

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

    def test_list_as_admin_or_ext_admin_elec_includes_elec_annotations(self):
        def setup_entity(email, entity):
            setup_current_user(self, email, "Admin", "test", [(entity, "RW")], True)
            response = self.client.get(reverse("entity-list") + f"?entity_id={entity.id}&q=CPO 1")
            entities_data = response.json()
            entity_data = entities_data[0]
            self.assertEqual(entity_data["charge_points_accepted"], 2)
            self.assertEqual(entity_data["charge_points_pending"], 1)
            self.assertEqual(entity_data["meter_readings_accepted"], 1)
            self.assertEqual(entity_data["meter_readings_pending"], 2)

        """Test that admin and external admin elec sees elec annotations (charge_points and meter_readings)"""
        setup_entity("admin@test.com", self.admin)
        setup_entity("elec_admin@test.com", self.ext_admin_elec)

    def test_list_as_not_admin_or_ext_admin_elec_does_not_include_elec_annotations(self):
        """Test that not admin and not external admin elec does not see elec annotations"""
        setup_current_user(
            self, "ext_admin_airline@test.com", "Airline Admin", "test", [(self.ext_admin_airline, "RW")], True
        )
        # This case is not possible because an external admin cannot have elec applications and meter readings
        # But we want to check if the endpoint does not return the data related to elec if we're not an admin
        # or an external admin elec
        add_elec_applications_and_meter_readings_to_entity(self.ext_admin_airline)

        response = self.client.get(reverse("entity-list") + f"?entity_id={self.ext_admin_airline.id}&q=Airline 1")

        entities_data = response.json()
        entity_data = entities_data[0]
        self.assertEqual(entity_data["charge_points_accepted"], 0)
        self.assertEqual(entity_data["charge_points_pending"], 0)
        self.assertEqual(entity_data["meter_readings_accepted"], 0)
        self.assertEqual(entity_data["meter_readings_pending"], 0)

    def test_list_as_admin_includes_admin_only_annotations(self):
        """Test that only admin sees admin annotations (depots, production_sites, certificates, double_counting)"""
        setup_current_user(self, "admin@test.com", "Admin", "test", [(self.admin, "RW")], True)
        cert = GenericCertificateFactory.create(certificate_id="FR_123")
        EntityCertificateFactory.create(entity=self.admin, certificate=cert, checked_by_admin=False, rejected_by_admin=False)
        EntityCertificateFactory.create(entity=self.admin, certificate=cert, checked_by_admin=True, rejected_by_admin=False)
        EntityCertificateFactory.create(entity=self.admin, certificate=cert, checked_by_admin=False, rejected_by_admin=True)
        EntityCertificateFactory.create(entity=self.admin, certificate=cert, checked_by_admin=True, rejected_by_admin=True)

        response = self.client.get(reverse("entity-list") + f"?entity_id={self.admin.id}&q=Admin Entity")

        entities_data = response.json()
        admin_entity_data = entities_data[0]
        self.assertEqual(admin_entity_data["certificates"], 4)
        self.assertEqual(admin_entity_data["certificates_pending"], 1)

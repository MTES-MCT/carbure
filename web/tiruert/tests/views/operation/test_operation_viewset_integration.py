from django.test import TestCase
from django.urls import reverse

from core.models import Biocarburant, Entity, MatierePremiere
from core.tests_utils import setup_current_user
from tiruert.models import Operation, OperationDetail
from transactions.factories import CarbureLotFactory
from transactions.models import Depot


class OperationViewSetIntegrationTest(TestCase):
    """Test OperationViewSet CRUD operations."""

    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/depots.json",
        "json/entities_sites.json",
    ]

    @classmethod
    def setUpTestData(cls):
        """Create test data once for the entire test class."""
        # Get references from fixtures
        cls.entity = Entity.objects.filter(entity_type=Entity.OPERATOR).first()
        cls.other_entity = Entity.objects.filter(entity_type=Entity.OPERATOR).exclude(id=cls.entity.id).first()
        cls.depot = Depot.objects.first()
        cls.feedstock_conv = MatierePremiere.biofuel.filter(category="CONV").first()
        cls.biofuel_eth = Biocarburant.objects.get(code="ETH")

        # Create TIRUERT operations directly for testing ViewSet
        # Operation 1: INCORPORATION (VALIDATED)
        cls.operation_incorporation = Operation.objects.create(
            type=Operation.INCORPORATION,
            status=Operation.VALIDATED,
            customs_category=MatierePremiere.CONV,
            biofuel=cls.biofuel_eth,
            credited_entity=cls.entity,
            to_depot=cls.depot,
            renewable_energy_share=1.0,
        )

        # Operation 2: MAC_BIO (VALIDATED)
        cls.operation_mac_bio = Operation.objects.create(
            type=Operation.MAC_BIO,
            status=Operation.VALIDATED,
            customs_category=MatierePremiere.CONV,
            biofuel=cls.biofuel_eth,
            credited_entity=cls.entity,
            to_depot=cls.depot,
            renewable_energy_share=1.0,
        )

        # Operation 3: LIVRAISON_DIRECTE (VALIDATED)
        cls.operation_livraison = Operation.objects.create(
            type=Operation.LIVRAISON_DIRECTE,
            status=Operation.VALIDATED,
            customs_category=MatierePremiere.CONV,
            biofuel=cls.biofuel_eth,
            credited_entity=cls.entity,
            to_depot=cls.depot,
            renewable_energy_share=1.0,
        )

        # Operation 4: CESSION (PENDING)
        cls.operation_cession = Operation.objects.create(
            type=Operation.CESSION,
            status=Operation.PENDING,
            customs_category=MatierePremiere.CONV,
            biofuel=cls.biofuel_eth,
            credited_entity=cls.other_entity,
            debited_entity=cls.entity,
            to_depot=cls.depot,
            renewable_energy_share=1.0,
        )

        # Add OperationDetails to first operation for testing details endpoint
        cls.lot1 = CarbureLotFactory.create(
            carbure_client=cls.entity,
            feedstock=cls.feedstock_conv,
            biofuel=cls.biofuel_eth,
            lot_status="ACCEPTED",
            delivery_type="BLENDING",
            volume=1000,
            ghg_total=10.5,
        )
        cls.lot2 = CarbureLotFactory.create(
            carbure_client=cls.entity,
            feedstock=cls.feedstock_conv,
            biofuel=cls.biofuel_eth,
            lot_status="ACCEPTED",
            delivery_type="BLENDING",
            volume=2000,
            ghg_total=12.3,
        )

        # Create OperationDetails
        OperationDetail.objects.create(
            operation=cls.operation_incorporation, lot=cls.lot1, volume=500, emission_rate_per_mj=10.5
        )
        OperationDetail.objects.create(
            operation=cls.operation_incorporation, lot=cls.lot2, volume=1500, emission_rate_per_mj=12.3
        )

    def setUp(self):
        super().setUp()
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, "ADMIN")])
        self.url = reverse("operations-list")

    def test_list_operations_returns_all_operations(self):
        """Test GET /operations/ returns list of operations."""
        query = {"entity_id": self.entity.id}
        response = self.client.get(self.url, query)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("count", data)
        self.assertIn("results", data)
        self.assertEqual(data["count"], 4)

    def test_list_operations_with_details(self):
        """Test GET /operations/?details=1 includes operation details."""
        query = {"entity_id": self.entity.id, "details": 1}
        response = self.client.get(self.url, query)

        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        self.assertGreater(len(results), 0)
        self.assertIn("details", results[0])
        self.assertEqual(len(results[0]["details"]), 2)

    def test_list_operations_excludes_draft_credits(self):
        """Test GET /operations/ excludes draft operations that are credits."""
        # Create a draft operation that is a credit
        Operation.objects.create(
            type=Operation.CESSION,
            status=Operation.DRAFT,
            biofuel=self.biofuel_eth,
            credited_entity=self.entity,  # entity is credited, so it's a credit
            debited_entity=Entity.objects.exclude(id=self.entity.id).first(),
            to_depot=self.depot,
            customs_category=MatierePremiere.CONV,
            renewable_energy_share=1.0,
        )

        query = {"entity_id": self.entity.id}
        response = self.client.get(self.url, query)

        self.assertEqual(response.status_code, 200)
        # Should still be 4 because draft credit is excluded
        self.assertEqual(response.json()["count"], 4)

    def test_partial_update_operation_updates_and_returns_operation(self):
        """Test PATCH /operations/:id/ updates operation."""
        operation = Operation.objects.create(
            type=Operation.CESSION,
            status=Operation.PENDING,
            biofuel=self.biofuel_eth,
            debited_entity=self.entity,
            credited_entity=Entity.objects.exclude(id=self.entity.id).first(),
            to_depot=self.depot,
            customs_category=MatierePremiere.CONV,
            renewable_energy_share=1.0,
        )

        url = reverse("operations-detail", kwargs={"pk": operation.id})
        new_depot = Depot.objects.exclude(id=self.depot.id).first()
        payload = {"to_depot": new_depot.id}

        response = self.client.patch(
            url, data=payload, content_type="application/json", QUERY_STRING=f"entity_id={self.entity.id}"
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["to_depot"]["id"], new_depot.id)
        self.assertEqual(data["to_depot"]["name"], new_depot.name)

    def test_partial_update_status_changes_operation_status(self):
        """Test PATCH /operations/:id/ can update status."""
        operation = Operation.objects.create(
            type=Operation.CESSION,
            status=Operation.DRAFT,
            biofuel=self.biofuel_eth,
            debited_entity=self.entity,
            credited_entity=Entity.objects.exclude(id=self.entity.id).first(),
            to_depot=self.depot,
            customs_category=MatierePremiere.CONV,
            renewable_energy_share=1.0,
        )

        url = reverse("operations-detail", kwargs={"pk": operation.id})
        payload = {"status": Operation.PENDING}

        response = self.client.patch(
            url, data=payload, content_type="application/json", QUERY_STRING=f"entity_id={self.entity.id}"
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], Operation.PENDING)

    def test_destroy_operation_with_valid_conditions(self):
        """Test DELETE /operations/:id/ deletes operation when conditions met."""
        # Create operation that can be deleted
        operation = Operation.objects.create(
            type=Operation.CESSION,
            status=Operation.PENDING,
            biofuel=self.biofuel_eth,
            debited_entity=self.entity,
            credited_entity=Entity.objects.exclude(id=self.entity.id).first(),
            to_depot=self.depot,
            customs_category=MatierePremiere.CONV,
            renewable_energy_share=1.0,
        )

        url = reverse("operations-detail", kwargs={"pk": operation.id})

        response = self.client.delete(url, QUERY_STRING=f"entity_id={self.entity.id}")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Operation.objects.filter(id=operation.id).exists())

    def test_destroy_operation_with_invalid_type_returns_403(self):
        """Test DELETE /operations/:id/ returns 403 for non-deletable types."""
        # Create operation with type that cannot be deleted
        operation = Operation.objects.create(
            type=Operation.INCORPORATION,
            status=Operation.PENDING,
            biofuel=self.biofuel_eth,
            credited_entity=self.entity,
            to_depot=self.depot,
            customs_category=MatierePremiere.CONV,
            renewable_energy_share=1.0,
        )

        url = reverse("operations-detail", kwargs={"pk": operation.id})

        response = self.client.delete(url, QUERY_STRING=f"entity_id={self.entity.id}")

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Operation.objects.filter(id=operation.id).exists())

    def test_destroy_operation_with_invalid_status_returns_403(self):
        """Test DELETE /operations/:id/ returns 403 for non-deletable statuses."""
        # Create operation with status that cannot be deleted
        operation = Operation.objects.create(
            type=Operation.CESSION,
            status=Operation.ACCEPTED,
            biofuel=self.biofuel_eth,
            debited_entity=self.entity,
            credited_entity=Entity.objects.exclude(id=self.entity.id).first(),
            to_depot=self.depot,
            customs_category=MatierePremiere.CONV,
            renewable_energy_share=1.0,
        )

        url = reverse("operations-detail", kwargs={"pk": operation.id})

        response = self.client.delete(url, QUERY_STRING=f"entity_id={self.entity.id}")

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Operation.objects.filter(id=operation.id).exists())

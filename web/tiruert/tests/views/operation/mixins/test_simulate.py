from unittest.mock import patch

import numpy as np
from django.test import TestCase
from rest_framework import status
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from core.models import Biocarburant, Entity, MatierePremiere
from tiruert.services.teneur import TeneurServiceError
from tiruert.views.operation.mixins.simulate import SimulateActionMixin, SimulationError
from transactions.models import Depot


class SimulateActionMixinTest(TestCase):
    """Test SimulateActionMixin.simulate() action"""

    fixtures = [
        "json/biofuels.json",
        "json/countries.json",
        "json/entities.json",
        "json/depots.json",
    ]

    def setUp(self):
        self.factory = APIRequestFactory()
        self.entity = Entity.objects.filter(entity_type=Entity.OPERATOR).first()
        self.biofuel = Biocarburant.objects.first()
        self.depot = Depot.objects.first()

        # Create a mock view class using SimulateActionMixin
        class MockSimulateView(SimulateActionMixin):
            pass

        self.view = MockSimulateView()

    def _create_request(self, data, unit="l"):
        """Helper to create a DRF Request object with proper attributes"""
        django_request = self.factory.post("/api/operations/simulate/")
        request = Request(django_request)
        request._full_data = data  # Set parsed data before validation
        request.entity = self.entity
        request.unit = unit
        return request

    def _create_valid_data(self):
        """Helper to create valid simulation input data"""
        return {
            "biofuel": self.biofuel.id,
            "customs_category": MatierePremiere.CONV,
            "debited_entity": self.entity.id,
            "target_volume": 1000.0,
            "target_emission": 1.5,
        }

    @patch("tiruert.views.operation.mixins.simulate.TeneurService.prepare_data_and_optimize")
    def test_simulate_with_valid_data_returns_200(self, mock_service):
        """Test that simulate returns 200 with valid data"""
        mock_service.return_value = (
            {0: 100.0, 1: 900.0},  # selected_lots
            np.array([10, 11]),  # lot_ids
            0.5,  # fun
        )

        data = self._create_valid_data()
        request = self._create_request(data)
        response = self.view.simulate(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("tiruert.views.operation.mixins.simulate.TeneurService.prepare_data_and_optimize")
    def test_simulate_calls_service_with_correct_parameters(self, mock_service):
        """Test that simulate calls TeneurService.prepare_data_and_optimize with validated data only."""
        mock_service.return_value = ({0: 1000.0}, np.array([10]), 0.5)

        data = self._create_valid_data()
        request = self._create_request(data, unit="mj")
        self.view.simulate(request)

        mock_service.assert_called_once()
        call_args = mock_service.call_args[0]
        # First arg is validated_data dict
        self.assertEqual(call_args[0]["target_volume"], 1000.0)
        self.assertEqual(call_args[0]["target_emission"], 1.5)

    @patch("tiruert.views.operation.mixins.simulate.TeneurService.prepare_data_and_optimize")
    def test_simulate_constructs_detail_operations_data_correctly(self, mock_service):
        """Test that simulate correctly constructs detail_operations_data from service result"""
        mock_service.return_value = (
            {0: 100.0, 2: 200.0},  # selected_lots (indices 0 and 2)
            np.array([10, 11, 12]),  # lot_ids
            0.5,
        )

        data = self._create_valid_data()
        request = self._create_request(data)
        response = self.view.simulate(request)

        result = response.data
        self.assertEqual(len(result["selected_lots"]), 2)
        self.assertEqual(result["selected_lots"][0]["lot_id"], 10)
        self.assertEqual(float(result["selected_lots"][0]["volume"]), 100.0)
        self.assertEqual(result["selected_lots"][1]["lot_id"], 12)
        self.assertEqual(float(result["selected_lots"][1]["volume"]), 200.0)
        self.assertEqual(response.data["fun"], 0.50)

    @patch("tiruert.views.operation.mixins.simulate.TeneurService.prepare_data_and_optimize")
    def test_simulate_handles_service_value_error(self, mock_service):
        """Test that simulate returns 400 when service raises TeneurServiceError"""
        mock_service.side_effect = TeneurServiceError(TeneurServiceError.NO_SUITABLE_LOTS_FOUND)

        data = self._create_valid_data()
        request = self._create_request(data)
        response = self.view.simulate(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "NO_SUITABLE_LOTS_FOUND")

    @patch("tiruert.views.operation.mixins.simulate.TeneurService.prepare_data_and_optimize")
    def test_simulate_does_not_expose_internal_exception(self, mock_service):
        mock_service.side_effect = ValueError("secret optimizer dump")

        data = self._create_valid_data()
        request = self._create_request(data)
        response = self.view.simulate(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], SimulationError.SIMULATION_FAILED)
        self.assertNotIn("secret", str(response.data))

    def test_simulate_with_missing_required_field_returns_400(self):
        """Test that simulate returns 400 when required field is missing"""
        data = self._create_valid_data()
        del data["target_emission"]  # Remove required field

        request = self._create_request(data)
        response = self.view.simulate(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("target_emission", response.data)

    def test_simulate_with_invalid_field_type_returns_400(self):
        """Test that simulate returns 400 when field has invalid type"""
        data = self._create_valid_data()
        data["target_volume"] = "not_a_number"

        request = self._create_request(data)
        response = self.view.simulate(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("target_volume", response.data)

    @patch("tiruert.views.operation.mixins.simulate.TeneurService.prepare_data_and_optimize")
    def test_simulate_with_optional_fields(self, mock_service):
        """Test that simulate accepts optional fields"""
        mock_service.return_value = ({0: 1000.0}, np.array([10]), 0.5)

        data = self._create_valid_data()
        data["max_n_batches"] = 5
        data["enforced_volumes"] = [100, 200]
        data["unit"] = "mj"
        data["durability_period"] = ["2024", "2025"]
        data["origin_country"] = ["FR", "DE"]
        data["feedstock"] = ["COLZA", "TOURNESOL"]

        request = self._create_request(data)
        response = self.view.simulate(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("tiruert.views.operation.mixins.simulate.TeneurService.prepare_data_and_optimize")
    def test_simulate_passes_new_filters_to_service(self, mock_service):
        """Test that simulate passes durability_period, origin_country, feedstock to service"""
        mock_service.return_value = ({0: 1000.0}, np.array([10]), 0.5)

        data = self._create_valid_data()
        data["durability_period"] = ["2024"]
        data["origin_country"] = ["FR"]
        data["feedstock"] = ["COLZA"]

        request = self._create_request(data)
        self.view.simulate(request)

        call_data = mock_service.call_args[0][0]
        self.assertEqual(call_data["durability_period"], ["2024"])
        self.assertEqual(call_data["origin_country"], ["FR"])
        self.assertEqual(call_data["feedstock"], ["COLZA"])

    @patch("tiruert.views.operation.mixins.simulate.TeneurService.prepare_data_and_optimize")
    def test_simulate_with_empty_result(self, mock_service):
        """Test that simulate handles empty result from service"""
        mock_service.return_value = ({}, np.array([]), 0.0)

        data = self._create_valid_data()
        request = self._create_request(data)
        response = self.view.simulate(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["selected_lots"]), 0)
        self.assertEqual(response.data["fun"], 0.0)

    @patch("tiruert.services.teneur.TeneurService.prepare_data")
    def test_simulate_mj_target_matches_returned_selected_lots_total_energy(self, mock_prepare_data):
        """Test that target volume in MJ matches the total returned selected lot energy."""
        requested_target_liters = 30.0
        requested_target_mj = requested_target_liters * float(self.biofuel.pci_litre)

        mock_prepare_data.return_value = (
            np.array([100.0, 100.0]),
            np.array([50.0, 60.0]),
            np.array([10, 11]),
            None,
            requested_target_liters,
        )

        data = self._create_valid_data()
        data["target_volume"] = requested_target_mj
        data["target_emission"] = 0.0

        request = self._create_request(data, unit="mj")
        response = self.view.simulate(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        selected_lots = response.data["selected_lots"]
        total_selected_liters = sum(float(lot["volume"]) for lot in selected_lots)
        total_selected_energy_mj = total_selected_liters * float(self.biofuel.pci_litre)

        self.assertEqual(total_selected_energy_mj, requested_target_mj)


class SimulateMinMaxActionMixinTest(TestCase):
    """Test SimulateActionMixin.simulate_min_max() action"""

    fixtures = [
        "json/biofuels.json",
        "json/countries.json",
        "json/entities.json",
        "json/depots.json",
    ]

    def setUp(self):
        self.factory = APIRequestFactory()
        self.entity = Entity.objects.filter(entity_type=Entity.OPERATOR).first()
        self.biofuel = Biocarburant.objects.first()
        self.depot = Depot.objects.first()

        # Create a mock view class using SimulateActionMixin
        class MockSimulateView(SimulateActionMixin):
            pass

        self.view = MockSimulateView()

    def _create_request(self, data, unit="l"):
        """Helper to create a DRF Request object with proper attributes"""
        django_request = self.factory.post("/api/operations/simulate/min_max/")
        request = Request(django_request)
        request._full_data = data  # Set parsed data before validation
        request.entity = self.entity
        request.unit = unit
        return request

    def _create_valid_data(self):
        """Helper to create valid simulation min/max input data"""
        return {
            "biofuel": self.biofuel.id,
            "customs_category": MatierePremiere.CONV,
            "debited_entity": self.entity.id,
            "target_volume": 1000.0,
        }

    @patch("tiruert.views.operation.mixins.simulate.TeneurService.get_min_and_max_emissions")
    def test_simulate_min_max_with_valid_data_returns_200(self, mock_service):
        """Test that simulate_min_max returns 200 with valid data"""
        mock_service.return_value = (1.5, 3.2)  # min, max

        data = self._create_valid_data()
        request = self._create_request(data)
        response = self.view.simulate_min_max(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("tiruert.views.operation.mixins.simulate.TeneurService.get_min_and_max_emissions")
    def test_simulate_min_max_calls_service_with_correct_parameters(self, mock_service):
        """Test that simulate_min_max calls TeneurService.get_min_and_max_emissions with validated data only."""
        mock_service.return_value = (1.5, 3.2)

        data = self._create_valid_data()
        request = self._create_request(data, unit="kg")
        self.view.simulate_min_max(request)

        mock_service.assert_called_once()
        call_args = mock_service.call_args[0]
        # First arg is validated_data dict
        self.assertEqual(call_args[0]["target_volume"], 1000.0)

    @patch("tiruert.views.operation.mixins.simulate.TeneurService.get_min_and_max_emissions")
    def test_simulate_min_max_returns_min_and_max_emissions(self, mock_service):
        """Test that simulate_min_max returns min and max avoided emissions"""
        mock_service.return_value = (2.5, 4.8)

        data = self._create_valid_data()
        request = self._create_request(data)
        response = self.view.simulate_min_max(request)

        self.assertEqual(response.data["min_avoided_emissions"], 2.5)
        self.assertEqual(response.data["max_avoided_emissions"], 4.8)

    @patch("tiruert.views.operation.mixins.simulate.TeneurService.get_min_and_max_emissions")
    def test_simulate_min_max_handles_negative_values(self, mock_service):
        """Test that simulate_min_max handles negative avoided emissions"""
        mock_service.return_value = (-1.0, 0.5)

        data = self._create_valid_data()
        request = self._create_request(data)
        response = self.view.simulate_min_max(request)

        self.assertEqual(response.data["min_avoided_emissions"], -1.0)
        self.assertEqual(response.data["max_avoided_emissions"], 0.5)

    @patch("tiruert.views.operation.mixins.simulate.TeneurService.get_min_and_max_emissions")
    def test_simulate_min_max_handles_service_value_error(self, mock_service):
        """Test that simulate_min_max returns 400 when service raises TeneurServiceError"""
        mock_service.side_effect = TeneurServiceError(TeneurServiceError.INSUFFICIENT_INPUT_VOLUME)

        data = self._create_valid_data()
        request = self._create_request(data)
        response = self.view.simulate_min_max(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "INSUFFICIENT_INPUT_VOLUME")

    @patch("tiruert.views.operation.mixins.simulate.TeneurService.get_min_and_max_emissions")
    def test_simulate_min_max_does_not_expose_internal_exception(self, mock_service):
        mock_service.side_effect = ValueError("secret optimizer dump")

        data = self._create_valid_data()
        request = self._create_request(data)
        response = self.view.simulate_min_max(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], SimulationError.SIMULATION_FAILED)
        self.assertNotIn("secret", str(response.data))

    def test_simulate_min_max_with_missing_required_field_returns_400(self):
        """Test that simulate_min_max returns 400 when required field is missing"""
        data = self._create_valid_data()
        del data["target_volume"]  # Remove required field

        request = self._create_request(data)
        response = self.view.simulate_min_max(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("target_volume", response.data)

    def test_simulate_min_max_with_invalid_field_type_returns_400(self):
        """Test that simulate_min_max returns 400 when field has invalid type"""
        data = self._create_valid_data()
        data["target_volume"] = "invalid"

        request = self._create_request(data)
        response = self.view.simulate_min_max(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("target_volume", response.data)

    @patch("tiruert.views.operation.mixins.simulate.TeneurService.get_min_and_max_emissions")
    def test_simulate_min_max_with_optional_fields(self, mock_service):
        """Test that simulate_min_max accepts optional fields"""
        mock_service.return_value = (1.5, 3.2)

        data = self._create_valid_data()
        data["unit"] = "mj"
        data["from_depot"] = self.depot.id
        data["ges_bound_min"] = 0.5
        data["ges_bound_max"] = 2.0
        data["feedstock"] = ["COLZA", "TOURNESOL"]
        data["origin_country"] = ["FR", "DE"]
        data["durability_period"] = ["2024", "2025"]

        request = self._create_request(data)
        response = self.view.simulate_min_max(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("tiruert.views.operation.mixins.simulate.TeneurService.get_min_and_max_emissions")
    def test_simulate_min_max_passes_new_filters_to_service(self, mock_service):
        """Test that simulate_min_max passes feedstock, origin_country, durability_period to service"""
        mock_service.return_value = (1.5, 3.2)

        data = self._create_valid_data()
        data["feedstock"] = ["COLZA"]
        data["origin_country"] = ["FR"]
        data["durability_period"] = ["2024"]

        request = self._create_request(data)
        self.view.simulate_min_max(request)

        call_data = mock_service.call_args[0][0]
        self.assertEqual(call_data["feedstock"], ["COLZA"])
        self.assertEqual(call_data["origin_country"], ["FR"])
        self.assertEqual(call_data["durability_period"], ["2024"])

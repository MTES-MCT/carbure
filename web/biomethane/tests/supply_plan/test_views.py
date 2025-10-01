from unittest.mock import patch

from django.test import TestCase

from biomethane.views import BiomethaneSupplyPlanViewSet


class BiomethaneSupplyPlanViewSetTests(TestCase):
    @patch("biomethane.views.supply_plan.supply_plan.get_biomethane_permissions")
    def test_endpoints_permissions(self, mock_get_biomethane_permissions):
        """Test that the write actions are correctly defined"""
        viewset = BiomethaneSupplyPlanViewSet()
        viewset.action = "retrieve"

        viewset.get_permissions()

        mock_get_biomethane_permissions.assert_called_once_with([], "retrieve")

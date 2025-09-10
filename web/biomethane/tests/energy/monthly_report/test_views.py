from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from biomethane.models import BiomethaneEnergy, BiomethaneEnergyMonthlyReport
from biomethane.utils import get_declaration_period
from core.models import Entity
from core.tests_utils import assert_object_contains_data, setup_current_user


class BiomethaneEnergyMonthlyReportViewSetTests(TestCase):
    def setUp(self):
        """Initial setup for tests"""
        self.current_year = get_declaration_period()

        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

        # Create energy declaration
        self.energy = BiomethaneEnergy.objects.create(
            producer=self.producer_entity,
            year=self.current_year,
            status=BiomethaneEnergy.PENDING,
        )

        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "gogogo",
            [(self.producer_entity, "RW")],
        )

        self.monthly_report_url = reverse("biomethane-energy-monthly-report")
        self.base_params = {"entity_id": self.producer_entity.id}

        # Test data for creating monthly reports
        self.valid_monthly_reports_data = [
            {
                "month": 1,
                "injected_volume_nm3": 1000.0,
                "average_monthly_flow_nm3_per_hour": 50.0,
                "injection_hours": 20.0,
            },
            {
                "month": 2,
                "injected_volume_nm3": 1200.0,
                "average_monthly_flow_nm3_per_hour": 60.0,
                "injection_hours": 20.0,
            },
        ]

    def test_permission_boundary(self):
        """Test that only biomethane producers can access endpoints"""
        # Create a non-biomethane producer entity
        wrong_entity = Entity.objects.create(
            name="Wrong Entity",
            entity_type=Entity.OPERATOR,
        )

        wrong_url = self.monthly_report_url
        wrong_url += "?entity_id=" + str(wrong_entity.id)

        response = self.client.get(wrong_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_monthly_reports_success(self):
        """Test successful retrieval of monthly reports"""
        params = {**self.base_params, "year": self.current_year}

        # Create monthly reports
        for report in self.valid_monthly_reports_data:
            BiomethaneEnergyMonthlyReport.objects.create(
                energy=self.energy,
                **report,
            )

        response = self.client.get(self.monthly_report_url, params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        for i, report in enumerate(response.data):
            assert_object_contains_data(self, report, self.valid_monthly_reports_data[i])

    def test_create_monthly_reports_success(self):
        """Test successful creation of monthly reports"""
        response = self.client.put(
            self.monthly_report_url,
            self.valid_monthly_reports_data,
            content_type="application/json",
            query_params=self.base_params,
        )

        reports = BiomethaneEnergyMonthlyReport.objects.filter(energy=self.energy)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(reports.count(), 2)
        for i, report in enumerate(reports):
            assert_object_contains_data(self, report, self.valid_monthly_reports_data[i])

    def test_update_monthly_reports_success(self):
        """Test successful update of monthly reports"""
        # Create monthly reports
        for report in self.valid_monthly_reports_data:
            BiomethaneEnergyMonthlyReport.objects.create(energy=self.energy, **report)

        updated_monthly_reports_data = [
            {
                "month": 1,
                "injected_volume_nm3": 100.0,
                "average_monthly_flow_nm3_per_hour": 50.0,
                "injection_hours": 20.0,
            },
        ]

        response = self.client.put(
            self.monthly_report_url,
            updated_monthly_reports_data,
            content_type="application/json",
            query_params=self.base_params,
        )

        reports = BiomethaneEnergyMonthlyReport.objects.filter(energy=self.energy)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(reports.count(), 2)
        assert_object_contains_data(self, reports[0], updated_monthly_reports_data[0])
        assert_object_contains_data(self, reports[1], self.valid_monthly_reports_data[1])

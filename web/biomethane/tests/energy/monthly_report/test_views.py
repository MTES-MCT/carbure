from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from biomethane.factories.production_unit import BiomethaneProductionUnitFactory
from biomethane.models import BiomethaneEnergy, BiomethaneEnergyMonthlyReport
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from biomethane.views.energy.monthly_report import BiomethaneEnergyMonthlyReportViewSet
from core.models import Department, Entity, ExternalAdminRights
from core.tests_utils import assert_object_contains_data, setup_current_user
from entity.models import EntityScope


class BiomethaneEnergyMonthlyReportViewSetTests(TestCase):
    def setUp(self):
        """Initial setup for tests"""
        self.viewset = BiomethaneEnergyMonthlyReportViewSet()
        self.current_year = BiomethaneAnnualDeclarationService.get_current_declaration_year()

        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

        # Create energy declaration
        self.energy = BiomethaneEnergy.objects.create(
            producer=self.producer_entity,
            year=self.current_year,
        )

        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "gogogo",
            [(self.producer_entity, "RW")],
        )

        self.monthly_report_url = reverse("biomethane-energy-monthly-report")
        self.base_params = {"entity_id": self.producer_entity.id, "year": self.current_year}

        # Test data for creating monthly reports
        self.valid_monthly_reports_data = [
            {
                "month": 1,
                "injected_volume_nm3": 1000.0,
                "average_monthly_flow_nm3_per_hour": 50.0,
            },
            {
                "month": 2,
                "injected_volume_nm3": 1200.0,
                "average_monthly_flow_nm3_per_hour": 60.0,
            },
        ]

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

    def test_list_monthly_reports_error_with_producer_using_producer_id_param(self):
        """Test that a producer cannot use producer_id param to access another producer's reports (IDOR protection)."""
        producer_entity_2 = Entity.objects.create(
            name="Test Producer 2",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

        # Authenticated as self.producer_entity but requesting producer_entity_2's data via producer_id
        params = {**self.base_params, "producer_id": producer_entity_2.id}

        response = self.client.get(self.monthly_report_url, params)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_monthly_reports_with_dreal_and_producer_id(self):
        """Test DREAL can access monthly reports filtered by producer_id."""
        department = Department.objects.create(code_dept="77", name="Seine-et-Marne")
        BiomethaneProductionUnitFactory.create(producer=self.producer_entity, department=department)

        dreal = Entity.objects.create(name="Test DREAL", entity_type=Entity.EXTERNAL_ADMIN)
        ExternalAdminRights.objects.create(entity=dreal, right=ExternalAdminRights.DREAL)
        EntityScope.objects.create(
            entity=dreal,
            content_type=ContentType.objects.get_for_model(Department),
            object_id=department.id,
        )

        for report in self.valid_monthly_reports_data:
            BiomethaneEnergyMonthlyReport.objects.create(energy=self.energy, **report)

        setup_current_user(self, "dreal@carbure.local", "DREAL", "gogogo", [(dreal, "ADMIN")])

        params = {"entity_id": dreal.id, "year": self.current_year, "producer_id": self.producer_entity.id}
        response = self.client.get(self.monthly_report_url, params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

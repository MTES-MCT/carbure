from django.test.testcases import TestCase

from biomethane.models.biomethane_energy import BiomethaneEnergy
from biomethane.models.biomethane_energy_monthly_report import BiomethaneEnergyMonthlyReport
from biomethane.serializers.energy.monthly_report import BiomethaneEnergyMonthlyReportInputSerializer
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from core.models import Entity
from core.tests_utils import assert_object_contains_data


class BiomethaneEnergyMonthlyReportInputSerializerTests(TestCase):
    def setUp(self):
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )
        self.current_year = BiomethaneAnnualDeclarationService.get_declaration_period()
        self.energy = BiomethaneEnergy.objects.create(
            producer=self.producer_entity,
            year=self.current_year,
        )
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
                "average_monthly_flow_nm3_per_hour": 50.0,
                "injection_hours": 20.0,
            },
        ]

    def test_month_cannot_be_duplicated(self):
        # Tests that the serializer rejects data with duplicate months
        invalid_monthly_reports_data = [
            {
                "month": 1,
                "injected_volume_nm3": 1000.0,
                "average_monthly_flow_nm3_per_hour": 50.0,
                "injection_hours": 20.0,
            },
            {
                "month": 1,
                "injected_volume_nm3": 2000.0,
                "average_monthly_flow_nm3_per_hour": 60.0,
                "injection_hours": 20.0,
            },
        ]
        serializer = BiomethaneEnergyMonthlyReportInputSerializer(data=invalid_monthly_reports_data)
        self.assertFalse(serializer.is_valid())

    def test_energy_not_found(self):
        # Tests that the serializer rejects data when no energy declaration is found
        serializer = BiomethaneEnergyMonthlyReportInputSerializer(data=self.valid_monthly_reports_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("energy", serializer.errors)

    def test_create_monthly_reports(self):
        # Tests the creation of new monthly reports with valid data
        serializer = BiomethaneEnergyMonthlyReportInputSerializer(context={"energy": self.energy})

        validated_data = serializer.create(self.valid_monthly_reports_data)

        # check that the validated data is the same as the input data
        assert_object_contains_data(self, validated_data[0], self.valid_monthly_reports_data[0])

        # check that the data is saved in the database and that it is the same as the input data
        data = BiomethaneEnergyMonthlyReport.objects.filter(energy=self.energy)
        self.assertEqual(data.count(), len(self.valid_monthly_reports_data))
        for i, report in enumerate(data):
            assert_object_contains_data(self, report, self.valid_monthly_reports_data[i])

    def test_update_monthly_reports(self):
        # Tests the update of existing monthly reports with new data
        for report in self.valid_monthly_reports_data:
            BiomethaneEnergyMonthlyReport.objects.create(energy=self.energy, **report)
        serializer = BiomethaneEnergyMonthlyReportInputSerializer(context={"energy": self.energy})
        updated_monthly_reports_data = [
            {
                "month": 1,
                "injected_volume_nm3": 10,
                "average_monthly_flow_nm3_per_hour": 5.0,
                "injection_hours": 2.0,
            },
            {
                "month": 2,
                "injected_volume_nm3": 120.0,
                "average_monthly_flow_nm3_per_hour": 5.0,
                "injection_hours": 2.0,
            },
        ]

        validated_data = serializer.create(updated_monthly_reports_data)

        # check that the validated data is the same as the input data
        for i, report in enumerate(validated_data):
            assert_object_contains_data(self, report, updated_monthly_reports_data[i])

        # check that the data is saved in the database and that it is the same as the input data
        data = BiomethaneEnergyMonthlyReport.objects.filter(energy=self.energy)
        self.assertEqual(data.count(), len(updated_monthly_reports_data))
        for i, report in enumerate(data):
            assert_object_contains_data(self, report, updated_monthly_reports_data[i])

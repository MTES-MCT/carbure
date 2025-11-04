from django.test import TestCase

from biomethane.models import BiomethaneContract, BiomethaneProductionUnit
from biomethane.models.biomethane_energy import BiomethaneEnergy
from core.models import Entity


class BiomethaneEnergySignalsTests(TestCase):
    def setUp(self):
        """Initial configuration for tests"""
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

        self.buyer_entity = Entity.objects.create(
            name="Test Buyer",
            entity_type=Entity.OPERATOR,
        )

        self.base_energy_data = {
            "producer": self.producer_entity,
            "year": 2024,
        }

        self.contract = BiomethaneContract.objects.create(
            producer=self.producer_entity, buyer=self.buyer_entity, tariff_reference="2011"
        )
        self.production_unit = BiomethaneProductionUnit.objects.create(producer=self.producer_entity, unit_name="Test Unit")

    def test_biomethane_energy_signal_clears_malfunction_fields(self):
        """Test that malfunction fields are cleared when saving a BiomethaneEnergy with has_malfunctions=False
        AND injection_impossibility_hours is cleared when has_injection_difficulties_due_to_network_saturation is False"""

        # Create an energy with malfunctions
        energy = BiomethaneEnergy.objects.create(
            **self.base_energy_data,
            has_malfunctions=False,  # No malfunctions
            malfunction_cumulative_duration_days=5,
            malfunction_types=[BiomethaneEnergy.MALFUNCTION_TYPE_MAINTENANCE],
            malfunction_details="Test malfunction",
            has_injection_difficulties_due_to_network_saturation=False,
            injection_impossibility_hours=10,
        )

        energy.save()
        energy.refresh_from_db()

        # Verify that malfunction fields are cleared
        self.assertIsNone(energy.malfunction_cumulative_duration_days)
        self.assertIsNone(energy.malfunction_types)
        self.assertIsNone(energy.malfunction_details)

        # Verify that injection_impossibility_hours is cleared when
        # has_injection_difficulties_due_to_network_saturation is False
        self.assertIsNone(energy.injection_impossibility_hours)

    def test_biomethane_energy_signal_clears_malfunction_details_when_not_other(self):
        """Test that malfunction_details is cleared when malfunction_types does not contain OTHER"""

        energy = BiomethaneEnergy.objects.create(
            **self.base_energy_data,
            has_malfunctions=True,
            malfunction_types=[BiomethaneEnergy.MALFUNCTION_TYPE_MAINTENANCE],  # Not OTHER
            malfunction_details="Test malfunction details",
        )

        energy.save()
        energy.refresh_from_db()

        # Verify that malfunction_details is cleared
        self.assertIsNone(energy.malfunction_details)

    def test_production_unit_signal_clears_flaring_hours_without_flowmeter(self):
        """Test that flaring_operating_hours is cleared when FLARING_FLOWMETER is not in installed_meters"""

        # Create an energy with flaring_operating_hours
        energy = BiomethaneEnergy.objects.create(
            **self.base_energy_data,
            flaring_operating_hours=100.0,
        )
        # Modify the production unit to trigger the signal
        self.production_unit.installed_meters = [
            BiomethaneProductionUnit.BIOGAS_PRODUCTION_FLOWMETER,
            BiomethaneProductionUnit.PURIFICATION_FLOWMETER,
        ]

        self.production_unit.save()
        energy.refresh_from_db()

        # Verify that flaring_operating_hours is cleared
        self.assertIsNone(energy.flaring_operating_hours)

    def test_contract_signal_clears_old_tariff_fields(self):
        """Test that old tariff fields are cleared for unsupported references"""

        # Create an energy with fields that should be cleared
        energy = BiomethaneEnergy.objects.create(
            **self.base_energy_data,
            energy_used_for_digester_heating="Test energy",
            purified_biogas_quantity_nm3=500.0,
            purification_electric_consumption_kwe=50.0,
        )

        # Modify the contract to trigger the signal
        self.contract.tariff_reference = "2023"
        self.contract.save()
        energy.refresh_from_db()

        # Verify that old tariff fields are cleared
        self.assertIsNone(energy.energy_used_for_digester_heating)
        self.assertIsNone(energy.purified_biogas_quantity_nm3)
        self.assertIsNone(energy.purification_electric_consumption_kwe)

    def test_contract_signal_clears_new_tariff_fields_for_old_references(self):
        """Test that new tariff fields are cleared for old references"""

        # Create an energy with new tariff fields
        energy = BiomethaneEnergy.objects.create(
            **self.base_energy_data,
            energy_used_for_installation_needs="Test energy",
            self_consumed_biogas_nm3=200.0,
            total_unit_electric_consumption_kwe=75.0,
        )

        # Modify the contract to trigger the signal
        self.contract.tariff_reference = "2020"
        self.contract.save()

        energy.refresh_from_db()

        # Verify that new tariff related fields are cleared
        self.assertIsNone(energy.energy_used_for_installation_needs)
        self.assertIsNone(energy.self_consumed_biogas_nm3)
        self.assertIsNone(energy.total_unit_electric_consumption_kwe)

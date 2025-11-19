from django.test import TestCase

from elec.models import ElecProvisionCertificateQualicharge
from elec.serializers.elec_provision_certificate_qualicharge import (
    ProvisionCertificateBulkSerializer,
    ProvisionCertificateUpdateBulkSerializer,
)


class ProvisionCertificateBulkSerializerTest(TestCase):
    """Tests for ProvisionCertificateBulkSerializer"""

    def test_valid_data(self):
        """Test with valid data"""
        data = {
            "entity": "Test CPO",
            "siren": "123456789",
            "operational_units": [
                {
                    "code": "FR001",
                    "from": "2023-01-01",
                    "to": "2023-03-31",
                    "stations": [
                        {
                            "id": "FRXYZP123456",
                            "energy": 1000.5,
                            "is_controlled": True,
                        }
                    ],
                }
            ],
        }
        serializer = ProvisionCertificateBulkSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invalid_station_id_format(self):
        """Test with an invalid station ID format"""
        data = {
            "entity": "Test CPO",
            "siren": "123456789",
            "operational_units": [
                {
                    "code": "FR001",
                    "from": "2023-01-01",
                    "to": "2023-03-31",
                    "stations": [
                        {
                            "id": "INVALID",  # Must start with FR and have 3 letters
                            "energy": 1000.5,
                            "is_controlled": True,
                        }
                    ],
                }
            ],
        }
        serializer = ProvisionCertificateBulkSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_invalid_operational_unit_code(self):
        """Test with an operational unit code that is too short"""
        data = {
            "entity": "Test CPO",
            "siren": "123456789",
            "operational_units": [
                {
                    "code": "FR",  # Must be at least 5 characters
                    "from": "2023-01-01",
                    "to": "2023-03-31",
                    "stations": [],
                }
            ],
        }
        serializer = ProvisionCertificateBulkSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_empty_entity(self):
        """Test with empty entity name"""
        data = {
            "entity": "",
            "siren": "123456789",
            "operational_units": [],
        }
        serializer = ProvisionCertificateBulkSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("entity", serializer.errors)

    def test_siren_too_short(self):
        """Test with SIREN too short (< 9 characters)"""
        data = {
            "entity": "Test CPO",
            "siren": "12345",
            "operational_units": [],
        }
        serializer = ProvisionCertificateBulkSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("siren", serializer.errors)

    def test_operational_unit_code_too_long(self):
        """Test with operational unit code too long (> 5 characters)"""
        data = {
            "entity": "Test CPO",
            "siren": "123456789",
            "operational_units": [
                {
                    "code": "FR00123",  # Too long
                    "from": "2023-01-01",
                    "to": "2023-03-31",
                    "stations": [],
                }
            ],
        }
        serializer = ProvisionCertificateBulkSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("operational_units", serializer.errors)

    def test_invalid_date_format(self):
        """Test with invalid date format"""
        data = {
            "entity": "Test CPO",
            "siren": "123456789",
            "operational_units": [
                {
                    "code": "FR001",
                    "from": "invalid-date",
                    "to": "2023-03-31",
                    "stations": [],
                }
            ],
        }
        serializer = ProvisionCertificateBulkSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("operational_units", serializer.errors)

    def test_negative_energy(self):
        """Test with negative energy value"""
        data = {
            "entity": "Test CPO",
            "siren": "123456789",
            "operational_units": [
                {
                    "code": "FR001",
                    "from": "2023-01-01",
                    "to": "2023-03-31",
                    "stations": [
                        {
                            "id": "FRXYZP123456",
                            "energy": -100.0,  # Negative value
                            "is_controlled": True,
                        }
                    ],
                }
            ],
        }
        serializer = ProvisionCertificateBulkSerializer(data=data)
        # Le serializer accepte les valeurs négatives (pas de validation min_value)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invalid_is_controlled_type(self):
        """Test with invalid is_controlled value"""
        data = {
            "entity": "Test CPO",
            "siren": "123456789",
            "operational_units": [
                {
                    "code": "FR001",
                    "from": "2023-01-01",
                    "to": "2023-03-31",
                    "stations": [
                        {
                            "id": "FRXYZP123456",
                            "energy": 1000.0,
                            "is_controlled": "not_a_boolean",
                        }
                    ],
                }
            ],
        }
        serializer = ProvisionCertificateBulkSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("operational_units", serializer.errors)

    def test_station_id_too_short(self):
        """Test with station ID too short (< 7 characters)"""
        data = {
            "entity": "Test CPO",
            "siren": "123456789",
            "operational_units": [
                {
                    "code": "FR001",
                    "from": "2023-01-01",
                    "to": "2023-03-31",
                    "stations": [
                        {
                            "id": "FRXYZP",  # Too short
                            "energy": 1000.0,
                            "is_controlled": True,
                        }
                    ],
                }
            ],
        }
        serializer = ProvisionCertificateBulkSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("operational_units", serializer.errors)

    def test_missing_required_fields_comprehensive(self):
        """Test all missing required fields in a single call"""
        # Data with all required fields missing at different levels
        data = {
            # entity and siren missing at root level
            "operational_units": [
                {
                    # code, from, to missing at operational_unit level
                    "stations": [
                        {
                            # id, energy, is_controlled missing at station level
                        }
                    ],
                }
            ],
        }
        serializer = ProvisionCertificateBulkSerializer(data=data)
        self.assertFalse(serializer.is_valid())

        # Verify all root level required fields are in errors
        self.assertIn("entity", serializer.errors)
        self.assertIn("siren", serializer.errors)

        # Verify nested required fields are in operational_units errors
        self.assertIn("operational_units", serializer.errors)


class ProvisionCertificateUpdateBulkSerializerTest(TestCase):
    """Tests for ProvisionCertificateUpdateBulkSerializer"""

    def test_valid_data(self):
        """Test with valid data"""
        data = {
            "certificate_ids": [1, 2, 3],
            "validated_by": ElecProvisionCertificateQualicharge.CPO,
        }
        serializer = ProvisionCertificateUpdateBulkSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_empty_certificate_ids(self):
        """Test with an empty list of certificates"""
        data = {
            "certificate_ids": [],
            "validated_by": ElecProvisionCertificateQualicharge.DGEC,
        }
        serializer = ProvisionCertificateUpdateBulkSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("certificate_ids", serializer.errors)

    def test_invalid_validated_by(self):
        """Test with an invalid value for validated_by"""
        data = {
            "certificate_ids": [1, 2],
            "validated_by": "INVALID",
        }
        serializer = ProvisionCertificateUpdateBulkSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("validated_by", serializer.errors)

    def test_all_validation_choices(self):
        """Test that all validation choices are accepted"""
        for choice in [
            ElecProvisionCertificateQualicharge.NO_ONE,
            ElecProvisionCertificateQualicharge.CPO,
            ElecProvisionCertificateQualicharge.DGEC,
            ElecProvisionCertificateQualicharge.BOTH,
        ]:
            data = {
                "certificate_ids": [1],
                "validated_by": choice,
            }
            serializer = ProvisionCertificateUpdateBulkSerializer(data=data)
            self.assertTrue(serializer.is_valid(), f"Failed for choice: {choice}")

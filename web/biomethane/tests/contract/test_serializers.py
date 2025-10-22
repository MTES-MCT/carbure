from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from biomethane.models import BiomethaneContract
from biomethane.serializers import BiomethaneContractInputSerializer
from core.models import Entity


class BiomethaneContractSerializerTests(TestCase):
    """Unit tests for BiomethaneContractInputSerializer validation."""

    def setUp(self):
        """Initial setup for serializer validation tests."""
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

        self.buyer_entity = Entity.objects.create(
            name="Test Buyer",
            entity_type=Entity.OPERATOR,
        )

        self.context = {"entity": self.producer_entity}

        self.test_file = SimpleUploadedFile("test_contract.pdf", b"fake pdf content", content_type="application/pdf")

    def test_tariff_2011_required_fields_validation(self):
        """Test serializer validation for missing required fields (tariff 2011)."""
        data = {
            "tariff_reference": "2011",
            # Missing: buyer, installation_category, cmax, cmax_annualized
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("installation_category", serializer.errors)
        self.assertIn("cmax", serializer.errors)
        self.assertIn("cmax_annualized", serializer.errors)
        self.assertIn("buyer", serializer.errors)

    def test_tariff_2021_required_fields_validation(self):
        """Test serializer validation for missing required fields (tariff 2021)."""
        data = {
            "tariff_reference": "2021",
            # Missing: pap_contracted, buyer
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("pap_contracted", serializer.errors)
        self.assertIn("buyer", serializer.errors)

    def test_cmax_annualized_value_required_when_annualized_true(self):
        """Test serializer validation when cmax_annualized_value is required."""
        data = {
            "tariff_reference": "2011",
            "cmax_annualized": True,
            # Missing: cmax_annualized_value
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("cmax_annualized_value", serializer.errors)

    def test_invalid_installation_category(self):
        """Test serializer validation for invalid installation category."""
        data = {
            "installation_category": "INVALID_CATEGORY",
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("installation_category", serializer.errors)

    def test_invalid_tariff_reference(self):
        """Test serializer validation for invalid tariff reference."""
        data = {
            "tariff_reference": "INVALID_TARIFF",
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("tariff_reference", serializer.errors)

    def test_buyer_entity_exists_validation(self):
        """Test serializer validation for non-existent buyer entity."""
        data = {
            "buyer": 99999,  # Non-existent ID
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("buyer", serializer.errors)

    def test_valid_contract_creation_tariff_2011_2020(self):
        """Test serializer validation for valid tariff 2011 and 2020 contract."""

        for tariff in ["2011", "2020"]:
            data = {
                "tariff_reference": tariff,
                "buyer": self.buyer_entity.id,
                "installation_category": BiomethaneContract.INSTALLATION_CATEGORY_1,
                "cmax": 150.0,
                "cmax_annualized": True,
                "cmax_annualized_value": 150.0,
            }
            serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
            self.assertTrue(serializer.is_valid())

    def test_valid_contract_creation_tariff_2021_2023(self):
        """Test serializer validation for valid tariff 2021 and 2023 contract."""

        for tariff in ["2021", "2023"]:
            data = {
                "tariff_reference": tariff,
                "buyer": self.buyer_entity.id,
                "installation_category": BiomethaneContract.INSTALLATION_CATEGORY_1,
                "pap_contracted": 20.0,
            }

            serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
            self.assertTrue(serializer.is_valid())

    def test_missing_fields_if_signature_date_provided(self):
        """Test that providing signature_date requires effective_date and files."""

        data_with_signature_only = {
            "signature_date": "2022-01-15",
            # Missing: effective_date, general_conditions_file, specific_conditions_file
        }

        serializer = BiomethaneContractInputSerializer(data=data_with_signature_only, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("effective_date", serializer.errors)
        self.assertIn("general_conditions_file", serializer.errors)
        self.assertIn("specific_conditions_file", serializer.errors)

    # ========== TESTS FOR DATE VALIDATION ==========

    def test_effective_date_must_be_after_signature_date(self):
        """Test that effective_date must be after signature_date."""
        data = {
            "tariff_reference": "2023",
            "signature_date": "2022-01-15",
            "effective_date": "2022-01-10",  # Before signature_date
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("effective_date", serializer.errors)

    def test_signature_date_before_and_after_range(self):
        """Test signature date before valid range and after valid range for all tariffs."""

        wrong_signature_dates = [
            # (tariff, start_date, end_date)
            ("2011", "2011-11-22", "2020-11-24"),  # valid range 23/11/2011 - 23/11/2020
            ("2020", "2020-11-22", "2021-12-14"),  # valid range 23/11/2020 - 13/12/2021
            ("2021", "2021-12-12", "2023-06-13"),  # valid range 13/12/2021 - 10/06/2023
            ("2023", "2023-06-09", None),  # valid range after 10/06/2023
        ]

        for tariff, start_date, end_date in wrong_signature_dates:
            data_start = {
                "tariff_reference": tariff,
                "signature_date": start_date,
                "effective_date": "2024-01-01",
            }

            data_end = (
                {
                    "tariff_reference": tariff,
                    "signature_date": end_date,
                    "effective_date": "2024-01-01",
                }
                if end_date
                else None
            )

            for data in [data_start, data_end]:
                if data:
                    serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
                    self.assertFalse(serializer.is_valid())
                    self.assertIn("signature_date", serializer.errors)

    def test_tariff_2011_2020_signature_date_valid_range(self):
        """Test valid signature date range for tariff 2011 and 2020"""

        for tariff in ["2011", "2020"]:
            valid_date = "2015-06-15" if tariff == "2011" else "2021-06-15"
            data = {
                "tariff_reference": tariff,
                "buyer": self.buyer_entity.id,
                "installation_category": BiomethaneContract.INSTALLATION_CATEGORY_1,
                "cmax": 100.0,
                "cmax_annualized": False,
                "signature_date": valid_date,  # Valid date within range
                "effective_date": "2022-06-20",
                "general_conditions_file": self.test_file,
                "specific_conditions_file": self.test_file,
            }

            serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
            self.assertTrue(serializer.is_valid())

    def test_tariff_2021_2023_signature_date_valid_range(self):
        """Test valid signature date range for tariff 2021 and 2023"""

        for tariff in ["2021", "2023"]:
            valid_date = "2022-06-15" if tariff == "2021" else "2023-06-15"
            data = {
                "tariff_reference": tariff,
                "buyer": self.buyer_entity.id,
                "installation_category": BiomethaneContract.INSTALLATION_CATEGORY_1,
                "pap_contracted": 50.0,
                "signature_date": valid_date,  # Valid date within range
                "effective_date": "2024-06-20",
                "general_conditions_file": self.test_file,
                "specific_conditions_file": self.test_file,
            }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertTrue(serializer.is_valid())

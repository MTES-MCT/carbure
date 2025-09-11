from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from biomethane.models import BiomethaneContract
from biomethane.serializers import BiomethaneContractInputSerializer
from core.models import Entity


class BiomenthaneContractSerializerTests(TestCase):
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
            "buyer": self.buyer_entity.id,
            # Missing: installation_category, cmax, cmax_annualized
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("installation_category", serializer.errors)
        self.assertIn("cmax", serializer.errors)
        self.assertIn("cmax_annualized", serializer.errors)

    def test_tariff_2021_required_fields_validation(self):
        """Test serializer validation for missing required fields (tariff 2021)."""
        data = {
            "tariff_reference": "2021",
            "buyer": self.buyer_entity.id,
            # Missing: pap_contracted
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("pap_contracted", serializer.errors)

    def test_cmax_annualized_value_required_when_annualized_true(self):
        """Test serializer validation when cmax_annualized_value is required."""
        data = {
            "tariff_reference": "2011",
            "buyer": self.buyer_entity.id,
            "installation_category": BiomethaneContract.INSTALLATION_CATEGORY_1,
            "cmax": 100.0,
            "cmax_annualized": True,
            # Missing: cmax_annualized_value
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("cmax_annualized_value", serializer.errors)

    def test_invalid_installation_category(self):
        """Test serializer validation for invalid installation category."""
        data = {
            "tariff_reference": "2011",
            "buyer": self.buyer_entity.id,
            "installation_category": "INVALID_CATEGORY",
            "cmax": 100.0,
            "cmax_annualized": False,
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("installation_category", serializer.errors)

    def test_invalid_tariff_reference(self):
        """Test serializer validation for invalid tariff reference."""
        data = {
            "tariff_reference": "INVALID_TARIFF",
            "buyer": self.buyer_entity.id,
            "pap_contracted": 50.0,
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("tariff_reference", serializer.errors)

    def test_buyer_entity_exists_validation(self):
        """Test serializer validation for non-existent buyer entity."""
        data = {
            "tariff_reference": "2021",
            "buyer": 99999,  # Non-existent ID
            "pap_contracted": 50.0,
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("buyer", serializer.errors)

    def test_valid_contract_creation_tariff_2011(self):
        """Test serializer validation for valid tariff 2011 contract."""
        data = {
            "tariff_reference": "2011",
            "buyer": self.buyer_entity.id,
            "installation_category": BiomethaneContract.INSTALLATION_CATEGORY_1,
            "cmax": 150.0,
            "cmax_annualized": False,
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertTrue(serializer.is_valid())

    def test_valid_contract_creation_tariff_2021(self):
        """Test serializer validation for valid tariff 2021 contract."""
        data = {
            "tariff_reference": "2021",
            "buyer": self.buyer_entity.id,
            "pap_contracted": 20.0,
            "installation_category": BiomethaneContract.INSTALLATION_CATEGORY_1,
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertTrue(serializer.is_valid())

    def test_cmax_annualized_with_value_validation(self):
        """Test serializer validation when cmax_annualized is True with value."""
        data = {
            "tariff_reference": "2011",
            "buyer": self.buyer_entity.id,
            "installation_category": BiomethaneContract.INSTALLATION_CATEGORY_1,
            "cmax": 100.0,
            "cmax_annualized": True,
            "cmax_annualized_value": 150.0,
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertTrue(serializer.is_valid())

    def test_empty_required_fields_validation(self):
        """Test serializer validation for empty string values in required fields."""
        data = {}

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("tariff_reference", serializer.errors)

    def test_missing_fields_if_signature_date_provided(self):
        """Test that providing signature_date requires effective_date and files."""
        data_with_signature_only = {
            "tariff_reference": "2021",
            "buyer": self.buyer_entity.id,
            "pap_contracted": 50.0,
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
            "tariff_reference": "2021",
            "buyer": self.buyer_entity.id,
            "pap_contracted": 50.0,
            "signature_date": "2022-01-15",
            "effective_date": "2022-01-10",  # Before signature_date
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("effective_date", serializer.errors)

    def test_effective_date_equal_to_signature_date_invalid(self):
        """Test that effective_date equal to signature_date is invalid."""
        data = {
            "tariff_reference": "2021",
            "buyer": self.buyer_entity.id,
            "pap_contracted": 50.0,
            "signature_date": "2022-01-15",
            "effective_date": "2022-01-15",  # Same as signature_date
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("effective_date", serializer.errors)

    def test_tariff_2011_signature_date_valid_range(self):
        """Test valid signature date range for tariff 2011."""
        data = {
            "tariff_reference": "2011",
            "buyer": self.buyer_entity.id,
            "installation_category": BiomethaneContract.INSTALLATION_CATEGORY_1,
            "cmax": 100.0,
            "cmax_annualized": False,
            "signature_date": "2015-06-15",  # Valid date within range
            "effective_date": "2015-06-20",
            "general_conditions_file": self.test_file,
            "specific_conditions_file": self.test_file,
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertTrue(serializer.is_valid())

    def test_tariff_2011_signature_date_before_range(self):
        """Test signature date before valid range for tariff 2011."""
        data = {
            "tariff_reference": "2011",
            "buyer": self.buyer_entity.id,
            "installation_category": BiomethaneContract.INSTALLATION_CATEGORY_1,
            "cmax": 100.0,
            "cmax_annualized": False,
            "signature_date": "2011-11-22",  # Before 23/11/2011
            "effective_date": "2011-11-25",
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("signature_date", serializer.errors)

    def test_tariff_2011_signature_date_after_range(self):
        """Test signature date after valid range for tariff 2011."""
        data = {
            "tariff_reference": "2011",
            "buyer": self.buyer_entity.id,
            "installation_category": BiomethaneContract.INSTALLATION_CATEGORY_1,
            "cmax": 100.0,
            "cmax_annualized": False,
            "signature_date": "2020-11-24",  # After 23/11/2020
            "effective_date": "2020-11-25",
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("signature_date", serializer.errors)

    def test_tariff_2020_signature_date_valid_range(self):
        """Test valid signature date range for tariff 2020."""
        data = {
            "tariff_reference": "2020",
            "buyer": self.buyer_entity.id,
            "installation_category": BiomethaneContract.INSTALLATION_CATEGORY_1,
            "cmax": 100.0,
            "cmax_annualized": False,
            "signature_date": "2021-06-15",  # Valid date within range
            "effective_date": "2021-06-20",
            "general_conditions_file": self.test_file,
            "specific_conditions_file": self.test_file,
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertTrue(serializer.is_valid())

    def test_tariff_2020_signature_date_before_range(self):
        """Test signature date before valid range for tariff 2020."""
        data = {
            "tariff_reference": "2020",
            "buyer": self.buyer_entity.id,
            "installation_category": BiomethaneContract.INSTALLATION_CATEGORY_1,
            "cmax": 100.0,
            "cmax_annualized": False,
            "signature_date": "2020-11-22",  # Before 23/11/2020
            "effective_date": "2020-11-25",
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("signature_date", serializer.errors)

    def test_tariff_2020_signature_date_after_range(self):
        """Test signature date after valid range for tariff 2020."""
        data = {
            "tariff_reference": "2020",
            "buyer": self.buyer_entity.id,
            "installation_category": BiomethaneContract.INSTALLATION_CATEGORY_1,
            "cmax": 100.0,
            "cmax_annualized": False,
            "signature_date": "2021-12-14",  # After 13/12/2021
            "effective_date": "2021-12-15",
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("signature_date", serializer.errors)

    def test_tariff_2021_signature_date_valid_range(self):
        """Test valid signature date range for tariff 2021."""
        data = {
            "tariff_reference": "2021",
            "buyer": self.buyer_entity.id,
            "installation_category": BiomethaneContract.INSTALLATION_CATEGORY_1,
            "pap_contracted": 50.0,
            "signature_date": "2022-06-15",  # Valid date within range
            "effective_date": "2022-06-20",
            "general_conditions_file": self.test_file,
            "specific_conditions_file": self.test_file,
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertTrue(serializer.is_valid())

    def test_tariff_2021_signature_date_before_range(self):
        """Test signature date before valid range for tariff 2021."""
        data = {
            "tariff_reference": "2021",
            "buyer": self.buyer_entity.id,
            "pap_contracted": 50.0,
            "signature_date": "2021-12-12",  # Before 13/12/2021
            "effective_date": "2021-12-15",
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("signature_date", serializer.errors)

    def test_tariff_2021_signature_date_after_range(self):
        """Test signature date after valid range for tariff 2021."""
        data = {
            "tariff_reference": "2021",
            "buyer": self.buyer_entity.id,
            "pap_contracted": 50.0,
            "signature_date": "2023-06-11",  # After 10/06/2023
            "effective_date": "2023-06-15",
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("signature_date", serializer.errors)

    def test_tariff_2023_signature_date_valid(self):
        """Test valid signature date for tariff 2023."""
        data = {
            "tariff_reference": "2023",
            "buyer": self.buyer_entity.id,
            "installation_category": BiomethaneContract.INSTALLATION_CATEGORY_1,
            "pap_contracted": 50.0,
            "signature_date": "2023-06-15",  # After 10/06/2023
            "effective_date": "2023-06-20",
            "general_conditions_file": self.test_file,
            "specific_conditions_file": self.test_file,
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertTrue(serializer.is_valid())

    def test_tariff_2023_signature_date_before_threshold(self):
        """Test signature date before threshold for tariff 2023."""
        data = {
            "tariff_reference": "2023",
            "buyer": self.buyer_entity.id,
            "pap_contracted": 50.0,
            "signature_date": "2023-06-10",  # Not after 10/06/2023 (equal)
            "effective_date": "2023-06-15",
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("signature_date", serializer.errors)

    def test_tariff_range_validation_at_boundaries(self):
        """Test tariff date validation at exact boundaries."""
        # Tariff 2011 - exact start boundary
        data = {
            "tariff_reference": "2011",
            "buyer": self.buyer_entity.id,
            "installation_category": BiomethaneContract.INSTALLATION_CATEGORY_1,
            "cmax": 100.0,
            "cmax_annualized": False,
            "signature_date": "2011-11-23",  # Exactly at start boundary
            "effective_date": "2011-11-25",
            "general_conditions_file": self.test_file,
            "specific_conditions_file": self.test_file,
        }

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertTrue(serializer.is_valid())

        # Tariff 2011 - exact end boundary
        data["signature_date"] = "2020-11-23"  # Exactly at end boundary
        data["effective_date"] = "2020-11-25"

        serializer = BiomethaneContractInputSerializer(data=data, context=self.context)
        self.assertTrue(serializer.is_valid())

    # ========== TESTS FOR IS_RED_II HANDLER ==========

    def test_handle_is_red_ii_disables_when_cmax_below_threshold(self):
        """Test that handle_is_red_ii disables Red II when cmax <= 200 and user wants to disable."""
        # Setup producer with Red II enabled
        self.producer_entity.is_red_ii = True
        self.producer_entity.save()

        validated_data = {
            "cmax": 150.0,  # Below threshold
            "is_red_ii": False,  # User wants to disable
        }

        serializer = BiomethaneContractInputSerializer(context=self.context)
        serializer.handle_is_red_ii(validated_data, self.producer_entity)

        self.producer_entity.refresh_from_db()
        self.assertFalse(self.producer_entity.is_red_ii)
        self.assertNotIn("is_red_ii", validated_data)

    def test_handle_is_red_ii_disables_when_pap_below_threshold(self):
        """Test that handle_is_red_ii disables Red II when pap_contracted <= 19.5."""
        self.producer_entity.is_red_ii = True
        self.producer_entity.save()

        validated_data = {
            "pap_contracted": 15.0,  # Below threshold
            "is_red_ii": False,
        }

        serializer = BiomethaneContractInputSerializer(context=self.context)
        serializer.handle_is_red_ii(validated_data, self.producer_entity)

        self.producer_entity.refresh_from_db()
        self.assertFalse(self.producer_entity.is_red_ii)

    def test_handle_is_red_ii_no_change_when_above_threshold(self):
        """Test that handle_is_red_ii doesn't change Red II when values are above threshold."""
        self.producer_entity.is_red_ii = True
        self.producer_entity.save()

        validated_data = {
            "cmax": 250.0,  # Above threshold
            "is_red_ii": False,  # User wants to disable but can't
        }

        serializer = BiomethaneContractInputSerializer(context=self.context)
        serializer.handle_is_red_ii(validated_data, self.producer_entity)

        self.producer_entity.refresh_from_db()
        self.assertTrue(self.producer_entity.is_red_ii)  # Should remain True

    def test_handle_is_red_ii_no_change_when_is_red_ii_not_false(self):
        """Test that handle_is_red_ii only acts when is_red_ii is explicitly False."""
        self.producer_entity.is_red_ii = True
        self.producer_entity.save()

        validated_data = {
            "cmax": 150.0,  # Below threshold
            "is_red_ii": True,  # User doesn't want to disable
        }

        serializer = BiomethaneContractInputSerializer(context=self.context)
        serializer.handle_is_red_ii(validated_data, self.producer_entity)

        self.producer_entity.refresh_from_db()
        self.assertTrue(self.producer_entity.is_red_ii)  # Should remain True

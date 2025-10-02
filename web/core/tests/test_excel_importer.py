import io
from datetime import datetime
from unittest.mock import Mock, patch

import pandas as pd
from django.test import TestCase
from rest_framework import serializers

from core.excel_importer import ExcelImporter, ExcelValidationError
from entity.factories.entity import EntityFactory


class MockSerializer(serializers.Serializer):
    """Mock serializer for testing validation"""

    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    age = serializers.IntegerField(min_value=0)

    def create(self, validated_data):
        return validated_data


class ExcelImporterTestCase(TestCase):
    """Test cases for ExcelImporter class"""

    def setUp(self):
        """Set up test data"""
        self.sample_data = [
            {"name": "John Doe", "email": "john@example.com", "age": 30},
            {"name": "Jane Smith", "email": "jane@example.com", "age": 25},
            {"name": "Bob Johnson", "email": "bob@example.com", "age": 35},
        ]

    def create_test_excel_file(self, data=None, header_row=0):
        """Create a test Excel file with given data"""
        if data is None:
            data = self.sample_data

        df = pd.DataFrame(data)

        # Create a BytesIO object to simulate a file
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, startrow=header_row)

        excel_buffer.seek(0)
        return excel_buffer

    def test_parse_valid_excel_file(self):
        """Test parsing a valid Excel file"""
        excel_file = self.create_test_excel_file()

        result = ExcelImporter.parse(excel_file)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["name"], "John Doe")
        self.assertEqual(result[0]["email"], "john@example.com")
        self.assertEqual(result[0]["age"], 30)

    def test_parse_excel_file_with_custom_header_row(self):
        """Test parsing Excel file with custom header row"""
        excel_file = self.create_test_excel_file(header_row=2)

        result = ExcelImporter.parse(excel_file, header_row=2)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["name"], "John Doe")

    def test_parse_excel_file_with_nan_values(self):
        """Test parsing Excel file with NaN values and their conversion to None"""
        data_with_nan = [
            {"name": "John Doe", "email": "john@example.com", "age": 30},
            {"name": "Jane Smith", "email": None, "age": 25},  # Missing email -> should become None
            {"name": None, "email": "bob@example.com", "age": None},  # Missing name and age -> should become None
        ]

        excel_file = self.create_test_excel_file(data_with_nan)

        result = ExcelImporter.parse(excel_file)

        # Verify NaN values are properly converted to None for serializer compatibility
        self.assertEqual(len(result), 3)
        self.assertIsNone(result[1]["email"])
        self.assertIsNone(result[2]["name"])
        self.assertIsNone(result[2]["age"])

    @patch("pandas.read_excel")
    def test_parse_with_sheet_name(self, mock_read_excel):
        """Test parsing Excel file with specific sheet name"""
        mock_df = pd.DataFrame(self.sample_data)
        mock_read_excel.return_value = mock_df

        excel_file = io.BytesIO(b"fake excel content")

        ExcelImporter.parse(excel_file, sheet_name="Sheet2")

        mock_read_excel.assert_called_once_with(excel_file, header=0, sheet_name="Sheet2")

    @patch("pandas.read_excel")
    def test_parse_with_default_sheet_name(self, mock_read_excel):
        """Test parsing Excel file with default sheet name (None becomes 0)"""
        mock_df = pd.DataFrame(self.sample_data)
        mock_read_excel.return_value = mock_df

        excel_file = io.BytesIO(b"fake excel content")

        ExcelImporter.parse(excel_file)  # sheet_name defaults to None

        # Verify that None is converted to 0 (first sheet) by ExcelImporter logic
        mock_read_excel.assert_called_once_with(excel_file, header=0, sheet_name=0)

    def test_validate_retrieved_data_success(self):
        """Test successful validation returns the serializer unchanged"""
        serializer = MockSerializer(data=self.sample_data, many=True)
        config = {"header_row": 0}

        result = ExcelImporter.validate_retrieved_data(serializer, config, len(self.sample_data))

        self.assertTrue(result.is_valid())
        self.assertEqual(result, serializer)

    def test_validate_retrieved_data_exception_structure(self):
        """Test the structure and attributes of ExcelValidationError exception"""
        mock_serializer = Mock()
        mock_serializer.is_valid.return_value = False
        mock_serializer.errors = [
            {"field": ["Sample error message"]},
        ]

        config = {"header_row": 0}
        nb_rows = 5

        with self.assertRaises(ExcelValidationError) as context:
            ExcelImporter.validate_retrieved_data(mock_serializer, config, nb_rows)

        exception = context.exception

        # Test exception attributes
        self.assertEqual(exception.total_rows_processed, nb_rows)
        self.assertIsInstance(exception.validation_errors, list)

        # Test error structure
        error = exception.validation_errors[0]
        self.assertIn("row", error)
        self.assertIn("errors", error)
        self.assertIsInstance(error["row"], int)
        self.assertIsInstance(error["errors"], dict)

    def test_validate_retrieved_data_filters_empty_errors(self):
        """Test that validation only includes rows with errors, filtering out empty error dictionaries"""
        mock_serializer = Mock()
        mock_serializer.is_valid.return_value = False
        mock_serializer.errors = [
            {},  # Empty errors - should be filtered out
            {"name": ["Required field"]},  # Has errors - should be included
            {},  # Empty errors - should be filtered out
            {"email": ["Invalid email"]},  # Has errors - should be included
            {},  # Empty errors - should be filtered out
        ]

        config = {"header_row": 0}

        with self.assertRaises(ExcelValidationError) as context:
            ExcelImporter.validate_retrieved_data(mock_serializer, config, 5)

        exception = context.exception

        # Should only include the 2 rows that have actual errors
        self.assertEqual(len(exception.validation_errors), 2)

        # Verify the correct rows are included with correct Excel row numbers
        first_error = exception.validation_errors[0]
        self.assertEqual(first_error["row"], 3)  # Data row 1 -> Excel row 3
        self.assertIn("name", first_error["errors"])

        second_error = exception.validation_errors[1]
        self.assertEqual(second_error["row"], 5)  # Data row 3 -> Excel row 5
        self.assertIn("email", second_error["errors"])

    @patch("core.private_storage.save")
    @patch("core.excel_importer.datetime")
    def test_backup_file(self, mock_datetime, mock_storage_save):
        """Test file backup functionality"""
        # Mock datetime
        mock_now = datetime(2023, 10, 15, 14, 30, 45)
        mock_datetime.now.return_value = mock_now

        # Create mock file and entity
        mock_file = Mock()
        entity = EntityFactory(id=123, name="Test Entity")

        ExcelImporter.backup_file(mock_file, entity)

        # Verify storage.save was called with correct path
        expected_path = "biomethane/plans-approvisionnement/123_test-entity_20231015_143045.xlsx"
        mock_storage_save.assert_called_once_with(expected_path, mock_file)


class ExcelValidationErrorTestCase(TestCase):
    """Test cases for ExcelValidationError exception"""

    def test_excel_validation_error_initialization(self):
        """Test ExcelValidationError initialization"""
        validation_errors = [
            {"row": 2, "errors": {"name": ["This field is required."]}},
            {"row": 3, "errors": {"email": ["Enter a valid email address."]}},
        ]
        total_rows = 10

        exception = ExcelValidationError(validation_errors, total_rows)

        self.assertEqual(exception.validation_errors, validation_errors)
        self.assertEqual(exception.total_rows_processed, total_rows)
        self.assertEqual(str(exception), "Excel validation failed")

    def test_excel_validation_error_attributes(self):
        """Test that ExcelValidationError has correct attributes"""
        validation_errors = []
        total_rows = 5

        exception = ExcelValidationError(validation_errors, total_rows)

        self.assertTrue(hasattr(exception, "validation_errors"))
        self.assertTrue(hasattr(exception, "total_rows_processed"))
        self.assertIsInstance(exception, Exception)


class ExcelImporterIntegrationTestCase(TestCase):
    """Integration tests for ExcelImporter"""

    def test_full_workflow_with_valid_data(self):
        """Test complete workflow with valid data"""
        # Create test Excel file
        data = [
            {"name": "John Doe", "email": "john@example.com", "age": 30},
            {"name": "Jane Smith", "email": "jane@example.com", "age": 25},
        ]
        excel_file = self.create_test_excel_file(data)

        # Parse the file
        parsed_data = ExcelImporter.parse(excel_file)

        # Create and validate serializer
        serializer = MockSerializer(data=parsed_data, many=True)
        config = {"header_row": 0}

        # This should not raise an exception
        validated_serializer = ExcelImporter.validate_retrieved_data(serializer, config, len(parsed_data))

        self.assertEqual(validated_serializer, serializer)
        self.assertEqual(len(parsed_data), 2)

    def test_full_workflow_with_backup(self):
        """Test complete workflow including file backup"""
        data = [{"name": "Test User", "email": "test@example.com", "age": 30}]
        excel_file = self.create_test_excel_file(data)
        entity = EntityFactory()

        with patch("core.private_storage.save") as mock_save:
            # Parse and backup
            parsed_data = ExcelImporter.parse(excel_file)
            ExcelImporter.backup_file(excel_file, entity)

            # Verify backup was called
            mock_save.assert_called_once()

            # Verify parsed data
            self.assertEqual(len(parsed_data), 1)
            self.assertEqual(parsed_data[0]["name"], "Test User")

    def create_test_excel_file(self, data):
        """Helper method to create test Excel file"""
        df = pd.DataFrame(data)
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        excel_buffer.seek(0)
        return excel_buffer

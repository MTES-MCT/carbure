"""Tests for the supply plan Excel template creation service."""

from django.test import TestCase
from openpyxl import load_workbook

from biomethane.models import BiomethaneSupplyInput
from biomethane.services.supply_plan_excel_template import FRENCH_DEPARTMENTS, create_supply_plan_template


class SupplyPlanExcelTemplateTests(TestCase):
    """Tests for supply plan Excel template generation."""

    def test_create_supply_plan_template_creates_file(self):
        """Test that the Excel template is created successfully."""
        file = create_supply_plan_template()

        self.assertIsNotNone(file)
        self.assertTrue(file.readable())

    def test_template_has_all_required_sheets(self):
        """Test that all required sheets are present."""
        file = create_supply_plan_template()

        # Load workbook with openpyxl for inspection
        workbook = load_workbook(file)

        expected_sheets = [
            "Plan d'approvisionnement",
            "Provenance",
            "Type de culture",
            "Categories",
            "Unites",
            "Departements",
            "Pays",
        ]

        actual_sheets = workbook.sheetnames

        for sheet_name in expected_sheets:
            self.assertIn(sheet_name, actual_sheets, f"La feuille '{sheet_name}' devrait être présente")

    def test_main_sheet_has_correct_columns(self):
        """Test that the main sheet has the correct columns."""
        file = create_supply_plan_template()
        workbook = load_workbook(file)

        main_sheet = workbook["Plan d'approvisionnement"]

        expected_columns = [
            "Provenance",
            "Type de culture",
            "Catégorie",
            "Intrant",
            "Unité",
            "Ratio de matière sèche (%)",
            "Volume (tMB ou tMS)",
            "Pays d'origine",
            "Département",
            "Distance moyenne pondérée (km)",
            "Distance maximale (km)",
        ]

        # Read the first row (headers)
        actual_columns = [cell.value for cell in main_sheet[1]]

        self.assertEqual(actual_columns, expected_columns)

    def test_main_sheet_has_example_rows(self):
        """Test that the main sheet contains example rows."""
        file = create_supply_plan_template()
        workbook = load_workbook(file)

        main_sheet = workbook["Plan d'approvisionnement"]

        # Check that there are at least 2 example rows (+ 1 header row)
        self.assertGreaterEqual(main_sheet.max_row, 3)

        # Check that the first example row contains data
        self.assertIsNotNone(main_sheet.cell(2, 1).value)  # Provenance
        self.assertIsNotNone(main_sheet.cell(2, 7).value)  # Volume

    def test_provenance_sheet_has_correct_choices(self):
        """Test that the Provenance sheet contains the correct values."""
        file = create_supply_plan_template()
        workbook = load_workbook(file)

        provenance_sheet = workbook["Provenance"]

        # Check headers
        self.assertEqual(provenance_sheet.cell(1, 1).value, "Code")
        self.assertEqual(provenance_sheet.cell(1, 2).value, "Nom")

        # Check number of rows (header + 2 choices)
        expected_rows = 1 + len(BiomethaneSupplyInput.SOURCE_CHOICES)
        self.assertEqual(provenance_sheet.max_row, expected_rows)

        # Check values
        codes = [provenance_sheet.cell(i, 1).value for i in range(2, provenance_sheet.max_row + 1)]
        expected_codes = [choice[0] for choice in BiomethaneSupplyInput.SOURCE_CHOICES]
        self.assertEqual(codes, expected_codes)

    def test_crop_type_sheet_has_correct_choices(self):
        """Test that the Crop type sheet contains the correct values."""
        file = create_supply_plan_template()
        workbook = load_workbook(file)

        crop_type_sheet = workbook["Type de culture"]

        # Check number of rows
        expected_rows = 1 + len(BiomethaneSupplyInput.CROP_TYPE_CHOICES)
        self.assertEqual(crop_type_sheet.max_row, expected_rows)

    def test_categories_sheet_has_all_categories(self):
        """Test that the Categories sheet contains all categories."""
        file = create_supply_plan_template()
        workbook = load_workbook(file)

        categories_sheet = workbook["Categories"]

        # Check number of rows
        expected_rows = 1 + len(BiomethaneSupplyInput.INPUT_CATEGORY_CHOICES)
        self.assertEqual(categories_sheet.max_row, expected_rows)

        # Check codes
        codes = [categories_sheet.cell(i, 1).value for i in range(2, categories_sheet.max_row + 1)]
        expected_codes = [choice[0] for choice in BiomethaneSupplyInput.INPUT_CATEGORY_CHOICES]
        self.assertEqual(codes, expected_codes)

    def test_units_sheet_has_correct_units(self):
        """Test that the Units sheet contains the correct units."""
        file = create_supply_plan_template()
        workbook = load_workbook(file)

        units_sheet = workbook["Unites"]

        # Check number of rows
        expected_rows = 1 + len(BiomethaneSupplyInput.MATERIAL_UNIT_CHOICES)
        self.assertEqual(units_sheet.max_row, expected_rows)

    def test_departments_sheet_has_all_french_departments(self):
        """Test that the Departments sheet contains all French departments."""
        file = create_supply_plan_template()
        workbook = load_workbook(file)

        departments_sheet = workbook["Departements"]

        # Check number of rows (header + departments)
        expected_rows = 1 + len(FRENCH_DEPARTMENTS)
        self.assertEqual(departments_sheet.max_row, expected_rows)

        # Check some key departments
        codes = [departments_sheet.cell(i, 1).value for i in range(2, departments_sheet.max_row + 1)]
        self.assertIn("75", codes)  # Paris
        self.assertIn("2A", codes)  # Corse-du-Sud
        self.assertIn("971", codes)  # Guadeloupe

    def test_countries_sheet_has_data(self):
        """Test that the Countries sheet contains data."""
        file = create_supply_plan_template()
        workbook = load_workbook(file)

        countries_sheet = workbook["Pays"]

        # Check that there is data (at least France)
        self.assertGreater(countries_sheet.max_row, 1)

        # Check headers
        self.assertEqual(countries_sheet.cell(1, 1).value, "Code")
        self.assertEqual(countries_sheet.cell(1, 2).value, "Nom")

    def test_main_sheet_has_data_validations(self):
        """Test that the main sheet has data validation (dropdown lists)."""
        file = create_supply_plan_template()
        workbook = load_workbook(file)

        main_sheet = workbook["Plan d'approvisionnement"]

        # Check that data validations exist
        # Note: openpyxl reads data_validations as a DataValidationList
        validations = main_sheet.data_validations.dataValidation

        # Should have validations for: Provenance, Type de culture, Catégorie, Unité, Pays, Département
        self.assertGreater(len(validations), 0, "Should have data validations for dropdown lists")

        # Check specific validations by inspecting the sqref (cell ranges)
        validation_ranges = [v.sqref for v in validations]

        # Convert to strings for easier checking
        validation_ranges_str = [str(r) for r in validation_ranges]

        # Check that column A (Provenance) has validation
        has_col_a_validation = any("A2:A" in r for r in validation_ranges_str)
        self.assertTrue(has_col_a_validation, "Column A (Provenance) should have data validation")

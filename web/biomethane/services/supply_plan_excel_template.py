"""
Service to create an Excel template for the biomethane supply plan.
Uses xlsxwriter directly to support data validation (dropdown lists).
"""

from io import BufferedReader

import xlsxwriter

from biomethane.models import BiomethaneSupplyInput
from core.models import Department, Pays


def create_supply_plan_template() -> BufferedReader:
    """
    Creates an Excel template for the biomethane supply plan with data validation.

    The template contains:
    - A main sheet "Plan d'approvisionnement" with columns to fill and dropdown lists
    - Reference sheets for dropdown lists:
        - Departements (complete list)
        - Pays (from model)

    Returns:
        BufferedReader: Excel file ready to be downloaded
    """
    location = "/tmp/plan_approvisionnement_template.xlsx"
    workbook = xlsxwriter.Workbook(location)

    # Formats
    bold = workbook.add_format({"bold": True, "text_wrap": True})
    header_format = workbook.add_format({"bold": True, "text_wrap": True, "valign": "vcenter"})

    # Get countries from database
    eu_countries = list(Pays.objects.filter(is_in_europe=True).order_by("name"))
    # Get departments from database
    departments = list(Department.objects.all().order_by("code_dept"))

    # Create main sheet
    _create_main_sheet(workbook, header_format, eu_countries, departments)

    # Create reference sheets
    _create_departments_sheet(workbook, bold, departments)
    _create_countries_sheet(workbook, bold, eu_countries)

    workbook.close()
    return open(location, "rb")


def _create_main_sheet(workbook, header_format, countries, departments):
    """Create the main sheet with data validation."""
    sheet = workbook.add_worksheet("Plan d'approvisionnement")

    # Column headers
    headers = [
        ("Provenance", "source"),
        ("Catégorie", "input_category"),
        ("Intrant", "input_type"),
        ("Type de culture", "crop_type"),
        ("Unité", "material_unit"),
        ("Ratio de matière sèche (%)", "dry_matter_ratio_percent"),
        ("Volume (tMB ou tMS)", "volume"),
        ("Département", "origin_department"),
        ("Distance moyenne pondérée (km)", "average_weighted_distance_km"),
        ("Distance maximale (km)", "maximum_distance_km"),
        ("Pays d'origine", "origin_country"),
    ]

    # Write headers
    sheet.set_row(0, 30)
    for col, (header, key) in enumerate(headers):
        sheet.write(0, col, header, header_format)  # Visible header
        sheet.write(1, col, key)  # Hidden key row for reference
        sheet.set_column(col, col, 25)

    # Add all data validations
    _add_dropdown_validations(sheet, countries, departments)
    _add_numeric_validations(sheet)

    # Protect sheet and format columns
    _protect_and_format_sheet(workbook, sheet)


def _add_dropdown_validations(sheet, countries, departments):
    """Add dropdown list validations to the main sheet."""
    # Provenance (column A)
    provenance_labels = [label for _, label in BiomethaneSupplyInput.SOURCE_CHOICES]
    sheet.data_validation(
        "A3:A1000",
        {"validate": "list", "source": provenance_labels},
    )

    # Catégorie (column B)
    category_labels = [label for _, label in BiomethaneSupplyInput.INPUT_CATEGORY_CHOICES]
    sheet.data_validation(
        "B3:B1000",
        {"validate": "list", "source": category_labels},
    )

    # Type de culture (column D)
    crop_type_labels = [label for _, label in BiomethaneSupplyInput.CROP_TYPE_CHOICES]
    sheet.data_validation(
        "D3:D1000",
        {"validate": "list", "source": crop_type_labels},
    )

    # Unité (column E)
    unit_labels = [label for _, label in BiomethaneSupplyInput.MATERIAL_UNIT_CHOICES]
    sheet.data_validation(
        "E3:E1000",
        {"validate": "list", "source": unit_labels},
    )

    # Département (column H) - using reference sheet
    dept_count = len(departments)
    sheet.data_validation(
        "H3:H1000",
        {"validate": "list", "source": f"=Departements!$B$2:$B${dept_count + 1}"},
    )

    # Pays d'origine (column K) - using reference sheet
    countries_count = len(countries)
    sheet.data_validation(
        "K2:K1000",
        {"validate": "list", "source": f"=Pays!$B$2:$B${countries_count + 1}"},
    )


def _add_numeric_validations(sheet):
    """Add numeric validations with error messages to the main sheet."""
    # Ratio de matière sèche (column F) - must be a number between 0 and 100
    sheet.data_validation(
        "F3:F1000",
        {
            "validate": "decimal",
            "criteria": "between",
            "minimum": 0,
            "maximum": 100,
            "error_title": "Valeur invalide",
            "error_message": "Le ratio de matière sèche doit être un nombre entre 0 et 100.",
        },
    )

    # Volume (column G) - must be a positive number
    sheet.data_validation(
        "G3:G1000",
        {
            "validate": "decimal",
            "criteria": ">=",
            "value": 0,
            "error_title": "Valeur invalide",
            "error_message": "Le volume doit être un nombre positif.",
        },
    )

    # Distance moyenne pondérée (column I) - must be a positive number
    sheet.data_validation(
        "I3:I1000",
        {
            "validate": "decimal",
            "criteria": ">=",
            "value": 0,
            "error_title": "Valeur invalide",
            "error_message": "La distance moyenne doit être un nombre positif.",
        },
    )

    # Distance maximale (column J) - must be a positive number
    sheet.data_validation(
        "J3:J1000",
        {
            "validate": "decimal",
            "criteria": ">=",
            "value": 0,
            "error_title": "Valeur invalide",
            "error_message": "La distance maximale doit être un nombre positif.",
        },
    )


def _protect_and_format_sheet(workbook, sheet):
    """Protect the sheet and apply formatting to columns."""
    # Protect the sheet to prevent unhiding rows/columns
    sheet.protect(
        "",  # No password (or add one if needed)
        {
            "format_rows": False,  # Prevent unhiding rows
            "format_columns": False,  # Prevent unhiding columns
            "insert_rows": False,
            "delete_rows": False,
            "insert_columns": False,
            "delete_columns": False,
        },
    )

    # Hide the key row
    sheet.set_row(1, None, None, {"hidden": True})

    # Unlock data cells (rows 3 to 1000) so users can edit them
    unlocked = workbook.add_format({"locked": False})

    unlocked_decimal_number = workbook.add_format({"locked": False, "num_format": "0.0"})
    unlocked_number = workbook.add_format({"locked": False, "num_format": "0"})

    # Apply formats to columns
    for col in range(11):  # 11 columns (A to K)
        if col == 5:  # Column F: Ratio de matière sèche (%)
            sheet.set_column(col, col, 25, unlocked_decimal_number)
        elif col == 6:  # Column G: Volume (tMB ou tMS)
            sheet.set_column(col, col, 25, unlocked_decimal_number)
        elif col == 8:  # Column I: Distance moyenne pondérée (km)
            sheet.set_column(col, col, 25, unlocked_number)
        elif col == 9:  # Column J: Distance maximale (km)
            sheet.set_column(col, col, 25, unlocked_number)
        else:
            sheet.set_column(col, col, 25, unlocked)


def _create_departments_sheet(workbook, bold, departments):
    """Create the Departments reference sheet."""
    sheet = workbook.add_worksheet("Departements")
    sheet.write(0, 0, "Code", bold)
    sheet.write(0, 1, "Nom", bold)

    for row, dept in enumerate(departments, start=1):
        sheet.write(row, 0, dept.code_dept)
        sheet.write(row, 1, f"{dept.code_dept} - {dept.name}")

    sheet.hide()
    sheet.protect()


def _create_countries_sheet(workbook, bold, countries):
    """Create the Countries reference sheet."""
    sheet = workbook.add_worksheet("Pays")
    sheet.write(0, 0, "Code", bold)
    sheet.write(0, 1, "Nom", bold)

    for row, country in enumerate(countries, start=1):
        sheet.write(row, 0, country.code_pays)
        sheet.write(row, 1, country.name)

    sheet.hide()
    sheet.protect()

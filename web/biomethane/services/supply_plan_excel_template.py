"""
Service to create an Excel template for the biomethane supply plan.
Uses xlsxwriter directly to support data validation (dropdown lists).
"""

from io import BufferedReader

import xlsxwriter

from biomethane.models import BiomethaneSupplyInput
from core.models import Department, MatierePremiere, Pays


def create_supply_plan_template() -> BufferedReader:
    """
    Creates an Excel template for the biomethane supply plan with data validation.

    The template contains:
    - A main sheet "Plan d'approvisionnement" with columns to fill and dropdown lists
    - Reference sheets for dropdown lists:
        - Departements (from model)
        - Pays (from model)
        - Intrants (from model)

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
    # Get intrants from database
    inputs = list(MatierePremiere.biomethane.all().order_by("name"))

    # Create main sheet
    _create_main_sheet(workbook, header_format, eu_countries, departments, inputs)

    # Create reference sheets
    _create_departments_sheet(workbook, bold, departments)
    _create_countries_sheet(workbook, bold, eu_countries)
    _create_inputs_sheet(workbook, bold, inputs)

    workbook.close()
    return open(location, "rb")


def _create_main_sheet(workbook, header_format, countries, departments, inputs):
    """Create the main sheet with data validation."""
    sheet = workbook.add_worksheet("Plan d'approvisionnement")

    # Column headers
    headers = [
        ("Provenance", "source"),
        ("Intrant", "feedstock"),
        ("Type de CIVE", "type_cive"),
        ("Précisez la culture", "culture_details"),
        ("Type de collecte", "collection_type"),
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

    # Add formulas for automatic France country when department is selected
    _add_country_formulas(sheet, countries)

    # Add all data validations
    _add_dropdown_validations(sheet, countries, departments, inputs)
    _add_numeric_validations(sheet)

    # Protect sheet and format columns
    _protect_and_format_sheet(workbook, sheet)


def _add_country_formulas(sheet, countries):
    """
    Add formulas to automatically set France when a department is selected.
    The formula will overwrite empty value in the country column if a department is selected.
    """
    # Find France in the countries list
    france = next((c for c in countries if c.code_pays == "FR"), None)
    france_name = france.name if france else "France"

    # Add formula in column N (Pays d'origine) for rows 3 to 1000
    # If department (column K) is filled, force France, otherwise leave empty
    for row in range(2, 1000):
        formula = f'=IF(K{row+1}<>"","{france_name}","")'
        sheet.write_formula(row, 12, formula)  # column N (0-indexed = 12)


def _add_dropdown_validations(sheet, countries, departments, inputs):
    """Add dropdown list validations to the main sheet."""
    # Provenance (column A)
    provenance_labels = [label for _, label in BiomethaneSupplyInput.SOURCE_CHOICES]
    sheet.data_validation(
        "A3:A1000",
        {"validate": "list", "source": provenance_labels},
    )

    # Intrant (column B) - using reference sheet
    inputs_count = len(inputs)
    sheet.data_validation(
        "B3:B1000",
        {"validate": "list", "source": f"=Intrants!$A$2:$A${inputs_count + 1}"},
    )

    # Type de CIVE (column C)
    type_cive_labels = [label for _, label in BiomethaneSupplyInput.TYPE_CIVE_CHOICES]
    sheet.data_validation(
        "C3:C1000",
        {"validate": "list", "source": type_cive_labels},
    )

    # Précisez la culture (column D) - free text, no validation

    # Type de collecte (column E)
    collection_type_labels = [label for _, label in BiomethaneSupplyInput.COLLECTION_TYPE_CHOICES]
    sheet.data_validation(
        "E3:E1000",
        {"validate": "list", "source": collection_type_labels},
    )

    # Type de culture (column F)
    crop_type_labels = [label for _, label in BiomethaneSupplyInput.CROP_TYPE_CHOICES]
    sheet.data_validation(
        "F3:F1000",
        {"validate": "list", "source": crop_type_labels},
    )

    # Unité (column G)
    unit_labels = [label for _, label in BiomethaneSupplyInput.MATERIAL_UNIT_CHOICES]
    sheet.data_validation(
        "G3:G1000",
        {"validate": "list", "source": unit_labels},
    )

    # Département (column K) - using reference sheet
    dept_count = len(departments)
    sheet.data_validation(
        "K3:K1000",
        {"validate": "list", "source": f"=Departements!$B$2:$B${dept_count + 1}"},
    )

    # Pays d'origine (column N) - using reference sheet
    countries_count = len(countries)
    sheet.data_validation(
        "N2:N1000",
        {"validate": "list", "source": f"=Pays!$B$2:$B${countries_count + 1}"},
    )


def _add_numeric_validations(sheet):
    """Add numeric validations with error messages to the main sheet."""
    # Ratio de matière sèche (column H) - must be a number between 0 and 100
    sheet.data_validation(
        "H3:H1000",
        {
            "validate": "decimal",
            "criteria": "between",
            "minimum": 0,
            "maximum": 100,
            "error_title": "Valeur invalide",
            "error_message": "Le ratio de matière sèche doit être un nombre entre 0 et 100.",
        },
    )

    # Volume (column I) - must be a positive number
    sheet.data_validation(
        "I3:I1000",
        {
            "validate": "decimal",
            "criteria": ">=",
            "value": 0,
            "error_title": "Valeur invalide",
            "error_message": "Le volume doit être un nombre positif.",
        },
    )

    # Distance moyenne pondérée (column L) - must be a positive number
    sheet.data_validation(
        "L3:L1000",
        {
            "validate": "decimal",
            "criteria": ">=",
            "value": 0,
            "error_title": "Valeur invalide",
            "error_message": "La distance moyenne doit être un nombre positif.",
        },
    )

    # Distance maximale (column M) - must be a positive number
    sheet.data_validation(
        "M3:M1000",
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

    # Apply formats to columns (14 columns A to N)
    for col in range(14):
        if col == 7:  # Column H: Ratio de matière sèche (%)
            sheet.set_column(col, col, 25, unlocked_decimal_number)
        elif col == 8:  # Column I: Volume (tMB ou tMS)
            sheet.set_column(col, col, 25, unlocked_decimal_number)
        elif col == 11:  # Column L: Distance moyenne pondérée (km)
            sheet.set_column(col, col, 25, unlocked_number)
        elif col == 12:  # Column M: Distance maximale (km)
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


def _create_inputs_sheet(workbook, bold, feedstocks):
    """Create the Intrants reference sheet."""
    sheet = workbook.add_worksheet("Intrants")
    sheet.write(0, 0, "Nom", bold)

    for row, input in enumerate(feedstocks, start=1):
        sheet.write(row, 0, input.name)

    sheet.hide()
    sheet.protect()

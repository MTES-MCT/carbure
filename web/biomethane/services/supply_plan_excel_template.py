"""
Service to create an Excel template for the biomethane supply plan.
Uses xlsxwriter directly to support data validation (dropdown lists).
"""

from io import BufferedReader

import xlsxwriter

from biomethane.models import BiomethaneSupplyInput
from core.models import Pays

FRENCH_DEPARTMENTS = [
    ("01", "Ain"),
    ("02", "Aisne"),
    ("03", "Allier"),
    ("04", "Alpes-de-Haute-Provence"),
    ("05", "Hautes-Alpes"),
    ("06", "Alpes-Maritimes"),
    ("07", "Ardèche"),
    ("08", "Ardennes"),
    ("09", "Ariège"),
    ("10", "Aube"),
    ("11", "Aude"),
    ("12", "Aveyron"),
    ("13", "Bouches-du-Rhône"),
    ("14", "Calvados"),
    ("15", "Cantal"),
    ("16", "Charente"),
    ("17", "Charente-Maritime"),
    ("18", "Cher"),
    ("19", "Corrèze"),
    ("2A", "Corse-du-Sud"),
    ("2B", "Haute-Corse"),
    ("21", "Côte-d'Or"),
    ("22", "Côtes-d'Armor"),
    ("23", "Creuse"),
    ("24", "Dordogne"),
    ("25", "Doubs"),
    ("26", "Drôme"),
    ("27", "Eure"),
    ("28", "Eure-et-Loir"),
    ("29", "Finistère"),
    ("30", "Gard"),
    ("31", "Haute-Garonne"),
    ("32", "Gers"),
    ("33", "Gironde"),
    ("34", "Hérault"),
    ("35", "Ille-et-Vilaine"),
    ("36", "Indre"),
    ("37", "Indre-et-Loire"),
    ("38", "Isère"),
    ("39", "Jura"),
    ("40", "Landes"),
    ("41", "Loir-et-Cher"),
    ("42", "Loire"),
    ("43", "Haute-Loire"),
    ("44", "Loire-Atlantique"),
    ("45", "Loiret"),
    ("46", "Lot"),
    ("47", "Lot-et-Garonne"),
    ("48", "Lozère"),
    ("49", "Maine-et-Loire"),
    ("50", "Manche"),
    ("51", "Marne"),
    ("52", "Haute-Marne"),
    ("53", "Mayenne"),
    ("54", "Meurthe-et-Moselle"),
    ("55", "Meuse"),
    ("56", "Morbihan"),
    ("57", "Moselle"),
    ("58", "Nièvre"),
    ("59", "Nord"),
    ("60", "Oise"),
    ("61", "Orne"),
    ("62", "Pas-de-Calais"),
    ("63", "Puy-de-Dôme"),
    ("64", "Pyrénées-Atlantiques"),
    ("65", "Hautes-Pyrénées"),
    ("66", "Pyrénées-Orientales"),
    ("67", "Bas-Rhin"),
    ("68", "Haut-Rhin"),
    ("69", "Rhône"),
    ("70", "Haute-Saône"),
    ("71", "Saône-et-Loire"),
    ("72", "Sarthe"),
    ("73", "Savoie"),
    ("74", "Haute-Savoie"),
    ("75", "Paris"),
    ("76", "Seine-Maritime"),
    ("77", "Seine-et-Marne"),
    ("78", "Yvelines"),
    ("79", "Deux-Sèvres"),
    ("80", "Somme"),
    ("81", "Tarn"),
    ("82", "Tarn-et-Garonne"),
    ("83", "Var"),
    ("84", "Vaucluse"),
    ("85", "Vendée"),
    ("86", "Vienne"),
    ("87", "Haute-Vienne"),
    ("88", "Vosges"),
    ("89", "Yonne"),
    ("90", "Territoire de Belfort"),
    ("91", "Essonne"),
    ("92", "Hauts-de-Seine"),
    ("93", "Seine-Saint-Denis"),
    ("94", "Val-de-Marne"),
    ("95", "Val-d'Oise"),
    ("971", "Guadeloupe"),
    ("972", "Martinique"),
    ("973", "Guyane"),
    ("974", "La Réunion"),
    ("976", "Mayotte"),
]


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

    # Create main sheet
    _create_main_sheet(workbook, header_format, eu_countries)

    # Create reference sheets
    _create_departments_sheet(workbook, bold)
    _create_countries_sheet(workbook, bold, eu_countries)

    workbook.close()
    return open(location, "rb")


def _create_main_sheet(workbook, header_format, countries):
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
    _add_dropdown_validations(sheet, countries)
    _add_numeric_validations(sheet)

    # Protect sheet and format columns
    _protect_and_format_sheet(workbook, sheet)


def _add_dropdown_validations(sheet, countries):
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
    dept_count = len(FRENCH_DEPARTMENTS)
    sheet.data_validation(
        "H3:H1000",
        {"validate": "list", "source": f"=Departements!$B$2:$B${dept_count + 1}"},
    )

    # Pays d'origine (column K) - using reference sheet
    country_labels = [country.name for country in countries]
    sheet.data_validation(
        "K2:K1000",
        {"validate": "list", "source": country_labels},
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


def _create_departments_sheet(workbook, bold):
    """Create the Departments reference sheet."""
    sheet = workbook.add_worksheet("Departements")
    sheet.write(0, 0, "Code", bold)
    sheet.write(0, 1, "Nom", bold)

    for row, dept in enumerate(FRENCH_DEPARTMENTS, start=1):
        sheet.write(row, 0, dept[0])
        sheet.write(row, 1, f"{dept[0]} - {dept[1]}")

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

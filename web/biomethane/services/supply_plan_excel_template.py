"""
Service to create an Excel template for the biomethane supply plan.
Uses xlsxwriter directly to support data validation (dropdown lists).
"""

from io import BufferedReader

import xlsxwriter

from biomethane.models import BiomethaneSupplyInput
from biomethane.services.supply_plan.supply_input import COLLECTION_TYPE_REQUIRED_FEEDSTOCK_CODES
from core.models import Department, MatierePremiere, Pays


def create_supply_plan_template() -> BufferedReader:
    """
    Creates an Excel template for the biomethane supply plan with data validation.

    The template contains:
    - A main sheet "Plan d'approvisionnement" with a rules block at top (champs obligatoires
      selon l'intrant), then the table with columns to fill and dropdown lists
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
    rules_title_format = workbook.add_format(
        {
            "bold": True,
            "text_wrap": True,
            "bg_color": "#E8F4FC",
            "border": 1,
            "font_size": 12,
        }
    )
    rules_section_format = workbook.add_format(
        {
            "bold": True,
            "text_wrap": True,
            "bg_color": "#D4E8F2",
            "border": 1,
            "bottom": 2,
        }
    )
    rules_cell_format = workbook.add_format({"text_wrap": True, "border": 1})

    # Get countries from database
    eu_countries = list(Pays.objects.filter(is_in_europe=True).order_by("name"))
    # Get departments from database
    departments = list(Department.objects.all().order_by("code_dept"))
    # Get intrants from database (full list for dropdown; filtering for rule text is done in _create_main_sheet)
    inputs = list(MatierePremiere.biomethane.all().order_by("name"))

    # Create main sheet (with rules at top, then table)
    _create_main_sheet(
        workbook,
        header_format,
        rules_title_format,
        rules_section_format,
        rules_cell_format,
        eu_countries,
        departments,
        inputs,
    )

    # Create reference sheets
    _create_departments_sheet(workbook, bold, departments)
    _create_countries_sheet(workbook, bold, eu_countries)
    _create_inputs_sheet(workbook, bold, inputs)

    workbook.close()
    return open(location, "rb")


# Main sheet layout: rules block at top (with sections), then table (header, key row, data rows)
MAIN_SHEET_NUM_COLS = 11  # A to K
HEADER_ROW = 11  # 0-based
KEY_ROW = 12  # 0-based
FIRST_DATA_ROW = 13  # 0-based
LAST_DATA_ROW = 1012  # 0-based (1000 data rows)

# Table columns: (label, key). Type de CIVE, Précisez la culture, Type de collecte at the end.
TABLE_HEADERS = [
    ("Intrant", "feedstock"),
    ("Unité", "material_unit"),
    ("Ratio de matière sèche (%)", "dry_matter_ratio_percent"),
    ("Volume (tMB ou tMS)", "volume"),
    ("Département", "origin_department"),
    ("Distance moyenne pondérée (km)", "average_weighted_distance_km"),
    ("Distance maximale (km)", "maximum_distance_km"),
    ("Pays d'origine", "origin_country"),
    ("Type de CIVE", "type_cive"),
    ("Précisez la culture", "culture_details"),
    ("Type de collecte", "collection_type"),
]


def _build_collection_type_rule_text(inputs):
    """Build the rule text listing feedstocks that require 'Type de collecte' (with line breaks)."""
    names = [inp.name for inp in inputs if getattr(inp, "code", None) in COLLECTION_TYPE_REQUIRED_FEEDSTOCK_CODES]
    if not names:
        return (
            "• Si l'intrant est l'un des suivants (voir liste en base), "
            'le champ "Type de collecte" est obligatoire : (aucun dans la base).'
        )
    list_text = "\n".join(f"  • « {n} »" for n in sorted(names))
    return "• Si l'intrant est l'un des suivants, le champ \"Type de collecte\" est obligatoire :\n" f"{list_text}"


def _write_rules_block(sheet, num_cols, title_fmt, section_fmt, cell_fmt, inputs):
    """Write the rules block at top of sheet: title, two sections with bullet rules."""
    row = 0
    sheet.merge_range(row, 0, row, num_cols - 1, "Règles métier", title_fmt)
    sheet.set_row(row, 24)
    row += 1

    sheet.merge_range(
        row,
        0,
        row,
        num_cols - 1,
        "Selon l'intrant sélectionné, certains champs peuvent être obligatoires.",
        section_fmt,
    )
    row += 1
    intrant_rules = [
        "• Si l'intrant est une culture intermédiaire (CIVE) le champ Type de CIVE est obligatoire.",
        (
            "• Si l'intrant est « Autres cultures » ou « Autres cultures CIVE », "
            'le champ "Précisez la culture" est obligatoire.'
        ),
        _build_collection_type_rule_text(inputs),
        "• Si l'intrant est « Biogaz capté d'une ISDND », le champ Volume est optionnel.",
    ]
    for rule in intrant_rules:
        sheet.merge_range(row, 0, row, num_cols - 1, rule, cell_fmt)
        row += 1
    row += 1

    sheet.merge_range(row, 0, row, num_cols - 1, "Autres conditions :", section_fmt)
    row += 1
    other_rules = [
        (
            "• Si le pays d'origine est France, les champs « Distance moyenne pondérée », "
            "« Distance maximale » et « Département d'origine » sont obligatoires."
        ),
        "• Si l'unité de matière est « Sèche », le champ « Ratio de matière sèche (%) » est obligatoire.",
    ]
    for rule in other_rules:
        sheet.merge_range(row, 0, row, num_cols - 1, rule, cell_fmt)
        row += 1


def _write_table_header_and_key_row(sheet, header_fmt):
    """Write the table header row (labels) and the hidden key row (column keys for import)."""
    sheet.set_row(HEADER_ROW, 30)
    for col, (label, key) in enumerate(TABLE_HEADERS):
        sheet.write(HEADER_ROW, col, label, header_fmt)
        sheet.write(KEY_ROW, col, key)


def _create_main_sheet(
    workbook,
    header_format,
    rules_title_format,
    rules_section_format,
    rules_cell_format,
    countries,
    departments,
    inputs,
):
    """Create the main sheet with rules at top and data table below."""
    sheet = workbook.add_worksheet("Plan d'approvisionnement")
    num_cols = MAIN_SHEET_NUM_COLS
    sheet.set_column(0, num_cols - 1, 25)

    _write_rules_block(
        sheet,
        num_cols,
        rules_title_format,
        rules_section_format,
        rules_cell_format,
        inputs,
    )
    _write_table_header_and_key_row(sheet, header_format)

    _add_country_formulas(sheet, countries)
    _add_dropdown_validations(sheet, countries, departments, inputs)
    _add_numeric_validations(sheet)
    _protect_and_format_sheet(workbook, sheet)


def _add_country_formulas(sheet, countries):
    """
    Add formulas to automatically set France when a department is selected.
    Department is column E (index 4), country is column H (index 7).
    """
    france = next((c for c in countries if c.code_pays == "FR"), None)
    france_name = france.name if france else "France"

    for row in range(FIRST_DATA_ROW, LAST_DATA_ROW + 1):
        excel_row = row + 1
        formula = f'=IF(E{excel_row}<>"","{france_name}","")'
        sheet.write_formula(row, 7, formula)  # column H = Pays (0-indexed 7)


def _add_dropdown_validations(sheet, countries, departments, inputs):
    """Add dropdown list validations. Column order: A=Intrant, B=Unité, C=Ratio, D=Volume, E=Département, F=Dist moy, G=Dist
    max, H=Pays, I=Type CIVE, J=Précisez, K=Type collecte."""
    start_row = FIRST_DATA_ROW + 1  # Excel 1-based
    end_row = LAST_DATA_ROW + 1

    inputs_count = len(inputs)
    sheet.data_validation(
        f"A{start_row}:A{end_row}",
        {"validate": "list", "source": f"=Intrants!$A$2:$A${inputs_count + 1}"},
    )

    unit_labels = [label for _, label in BiomethaneSupplyInput.MATERIAL_UNIT_CHOICES]
    sheet.data_validation(
        f"B{start_row}:B{end_row}",
        {"validate": "list", "source": unit_labels},
    )

    dept_count = len(departments)
    sheet.data_validation(
        f"E{start_row}:E{end_row}",
        {"validate": "list", "source": f"=Departements!$B$2:$B${dept_count + 1}"},
    )

    countries_count = len(countries)
    sheet.data_validation(
        f"H{start_row}:H{end_row}",
        {"validate": "list", "source": f"=Pays!$B$2:$B${countries_count + 1}"},
    )

    type_cive_labels = [label for _, label in BiomethaneSupplyInput.TYPE_CIVE_CHOICES]
    sheet.data_validation(
        f"I{start_row}:I{end_row}",
        {"validate": "list", "source": type_cive_labels},
    )

    # J = Précisez la culture : free text, no validation

    collection_type_labels = [label for _, label in BiomethaneSupplyInput.COLLECTION_TYPE_CHOICES]
    sheet.data_validation(
        f"K{start_row}:K{end_row}",
        {"validate": "list", "source": collection_type_labels},
    )


def _add_numeric_validations(sheet):
    """Add numeric validations. C=Ratio, D=Volume, F=Dist moy, G=Dist max."""
    start_row = FIRST_DATA_ROW + 1
    end_row = LAST_DATA_ROW + 1

    sheet.data_validation(
        f"C{start_row}:C{end_row}",
        {
            "validate": "decimal",
            "criteria": "between",
            "minimum": 0,
            "maximum": 100,
            "error_title": "Valeur invalide",
            "error_message": "Le ratio de matière sèche doit être un nombre entre 0 et 100.",
        },
    )

    sheet.data_validation(
        f"D{start_row}:D{end_row}",
        {
            "validate": "decimal",
            "criteria": ">=",
            "value": 0,
            "error_title": "Valeur invalide",
            "error_message": "Le volume doit être un nombre positif.",
        },
    )

    sheet.data_validation(
        f"F{start_row}:F{end_row}",
        {
            "validate": "decimal",
            "criteria": ">=",
            "value": 0,
            "error_title": "Valeur invalide",
            "error_message": "La distance moyenne doit être un nombre positif.",
        },
    )

    sheet.data_validation(
        f"G{start_row}:G{end_row}",
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
    sheet.set_row(KEY_ROW, None, None, {"hidden": True})

    # Unlock data cells (rows 3 to 1000) so users can edit them
    unlocked = workbook.add_format({"locked": False})

    unlocked_decimal_number = workbook.add_format({"locked": False, "num_format": "0.0"})
    unlocked_number = workbook.add_format({"locked": False, "num_format": "0"})

    # Apply formats: C=Ratio (decimal), D=Volume (decimal), F=Dist moy (int), G=Dist max (int)
    for col in range(11):
        if col == 2:  # C: Ratio de matière sèche (%)
            sheet.set_column(col, col, 25, unlocked_decimal_number)
        elif col == 3:  # D: Volume (tMB ou tMS)
            sheet.set_column(col, col, 25, unlocked_decimal_number)
        elif col == 5:  # F: Distance moyenne pondérée (km)
            sheet.set_column(col, col, 25, unlocked_number)
        elif col == 6:  # G: Distance maximale (km)
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

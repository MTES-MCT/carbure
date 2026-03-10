"""
Service to create an Excel template for the biomethane supply plan.
Uses xlsxwriter directly to support data validation (dropdown lists).
"""

from io import BufferedReader

import xlsxwriter

from biomethane.models import BiomethaneSupplyInput
from biomethane.services.supply_plan.supply_input import COLLECTION_TYPE_REQUIRED_FEEDSTOCK_CODES
from core.models import Department, MatierePremiere, Pays

# Table columns: (label, key). CIVE type, culture details, collection type at the end.
TABLE_HEADERS = [
    ("Provenance", "source"),
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

# Main sheet layout: rules block at top (with sections), then table (header, key row, data rows)
MAIN_SHEET_NUM_COLS = len(TABLE_HEADERS)
HEADER_ROW = 12  # 0-based
KEY_ROW = 13  # 0-based
FIRST_DATA_ROW = 14  # 0-based
LAST_DATA_ROW = 1012  # 0-based (1000 data rows)
MAIN_SHEET_NAME = "Approvisionnement"


def _excel_column_letter(col_index: int) -> str:
    """Return Excel column letter(s) for 0-based index (0=A, 25=Z, 26=AA, ...)."""
    if col_index < 26:
        return chr(65 + col_index)
    return _excel_column_letter(col_index // 26 - 1) + chr(65 + col_index % 26)


# Derived from TABLE_HEADERS: no magic column indices or letters elsewhere
COLUMN_BY_KEY = {key: _excel_column_letter(i) for i, (_, key) in enumerate(TABLE_HEADERS)}
KEY_TO_COL_INDEX = {key: i for i, (_, key) in enumerate(TABLE_HEADERS)}

# Row height for wrapped text: Excel doesn't auto-expand; use this to size rows by line count
DEFAULT_POINTS_PER_LINE = 15
DEFAULT_MIN_ROW_HEIGHT = 24


def set_row_height_for_wrapped_text(
    sheet, row, text, *, min_height=DEFAULT_MIN_ROW_HEIGHT, points_per_line=DEFAULT_POINTS_PER_LINE
):
    """
    Set row height so that wrapped text (with newlines) is fully visible in Excel.
    Use before writing the cell. Reusable for any xlsxwriter sheet.
    """
    line_count = 1 + (text.count("\n") if text else 0)
    sheet.set_row(row, max(min_height, points_per_line * line_count))


def create_supply_plan_template() -> BufferedReader:
    """
    Creates an Excel template for the biomethane supply plan with data validation.

    The template contains:
    - A main sheet "Approvisionnement" with a rules block at top (required fields
      depending on feedstock), then the table with columns to fill and dropdown lists
    - Reference sheets for dropdown lists:
        - Departments (from model)
        - Countries (from model)
        - Feedstocks (from model)

    Returns:
        BufferedReader: Excel file ready to be downloaded
    """
    location = "/tmp/plan_approvisionnement_template.xlsx"
    workbook = xlsxwriter.Workbook(location)

    # Cell formats
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
    # Get feedstocks from database (full list for dropdown; filtering for rule text is done in _create_main_sheet)
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


def _build_collection_type_rule_text(inputs):
    """Build the rule text listing feedstocks that require 'Type de collecte' (collection type) with line breaks."""
    names = [inp.name for inp in inputs if getattr(inp, "code", None) in COLLECTION_TYPE_REQUIRED_FEEDSTOCK_CODES]
    col = COLUMN_BY_KEY["collection_type"]
    if not names:
        return (
            "• Si l'intrant est l'un des suivants (voir liste en base), "
            f'le champ "Type de collecte" (colonne {col}) est obligatoire : (aucun dans la base).'
        )
    list_text = "\n".join(f"  • « {n} »" for n in sorted(names))
    return (
        f"• Si l'intrant est l'un des suivants, le champ \"Type de collecte\" (colonne {col}) "
        f"est obligatoire :\n{list_text}"
    )


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
    c = COLUMN_BY_KEY
    intrant_rules = [
        (
            f"• Si l'intrant est une culture intermédiaire (CIVE) le champ Type de CIVE "
            f"(colonne {c['type_cive']}) est obligatoire."
        ),
        (
            "• Si l'intrant avec une nomenclature de type « XX - CIVE » n'est pas sélectionné, "
            "la culture est considérée par défaut comme une culture principale."
        ),
        (
            f"• Si l'intrant est « Autres cultures » ou « Autres cultures CIVE », "
            f'le champ "Précisez la culture" (colonne {c["culture_details"]}) est obligatoire.'
        ),
        _build_collection_type_rule_text(inputs),
        (
            f"• Si l'intrant est « Biogaz capté d'une ISDND », les champs Unité (colonne {c['material_unit']}), "
            f"Ratio de matière sèche (%) (colonne {c['dry_matter_ratio_percent']}) et Volume "
            f"(colonne {c['volume']}) sont optionnels."
        ),
    ]
    for rule in intrant_rules:
        set_row_height_for_wrapped_text(sheet, row, rule)
        sheet.merge_range(row, 0, row, num_cols - 1, rule, cell_fmt)
        row += 1
    row += 1

    sheet.merge_range(row, 0, row, num_cols - 1, "Autres conditions :", section_fmt)
    row += 1
    c = COLUMN_BY_KEY
    other_rules = [
        (
            f"• Si le pays d'origine est France, les champs « Distance moyenne pondérée » "
            f"(colonne {c['average_weighted_distance_km']}), « Distance maximale » "
            f"(colonne {c['maximum_distance_km']}) et « Département d'origine » "
            f"(colonne {c['origin_department']}) sont obligatoires."
        ),
        (
            f"• Si l'unité de matière est « Sèche », le champ « Ratio de matière sèche (%) » "
            f"(colonne {c['dry_matter_ratio_percent']}) est obligatoire."
        ),
    ]
    for rule in other_rules:
        set_row_height_for_wrapped_text(sheet, row, rule)
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
    sheet = workbook.add_worksheet(MAIN_SHEET_NAME)
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
    """Add formulas to set France when origin_department is selected (origin_country column)."""
    france = next((c for c in countries if c.code_pays == "FR"), None)
    france_name = france.name if france else "France"
    dept_col = COLUMN_BY_KEY["origin_department"]
    country_col_idx = KEY_TO_COL_INDEX["origin_country"]

    for row in range(FIRST_DATA_ROW, LAST_DATA_ROW + 1):
        excel_row = row + 1
        formula = f'=IF({dept_col}{excel_row}<>"","{france_name}","")'
        sheet.write_formula(row, country_col_idx, formula)


def _add_dropdown_validations(sheet, countries, departments, inputs):
    """Add dropdown validations from TABLE_HEADERS: column range and source derived by key."""
    start_row = FIRST_DATA_ROW + 1  # Excel 1-based
    end_row = LAST_DATA_ROW + 1
    inputs_count = len(inputs)
    dept_count = len(departments)
    countries_count = len(countries)

    # Key -> validation source (list of labels or sheet reference)
    dropdown_sources = {
        "feedstock": f"=Intrants!$A$2:$A${inputs_count + 1}",
        "material_unit": [label for _, label in BiomethaneSupplyInput.MATERIAL_UNIT_CHOICES],
        "origin_department": f"=Departements!$B$2:$B${dept_count + 1}",
        "origin_country": f"=Pays!$B$2:$B${countries_count + 1}",
        "type_cive": [label for _, label in BiomethaneSupplyInput.TYPE_CIVE_CHOICES],
        "collection_type": [label for _, label in BiomethaneSupplyInput.COLLECTION_TYPE_CHOICES],
        "source": [label for _, label in BiomethaneSupplyInput.SOURCE_CHOICES],
    }
    # culture_details: free text, no validation

    for key in COLUMN_BY_KEY:
        source = dropdown_sources.get(key)
        if source is None:
            continue
        col_letter = COLUMN_BY_KEY[key]
        cell_range = f"{col_letter}{start_row}:{col_letter}{end_row}"
        sheet.data_validation(cell_range, {"validate": "list", "source": source})


def _add_numeric_validations(sheet):
    """Add numeric validations by key (column range from COLUMN_BY_KEY)."""
    start_row = FIRST_DATA_ROW + 1
    end_row = LAST_DATA_ROW + 1

    validations = {
        "dry_matter_ratio_percent": {
            "validate": "decimal",
            "criteria": "between",
            "minimum": 0,
            "maximum": 100,
            "error_title": "Valeur invalide",
            "error_message": "Le ratio de matière sèche doit être un nombre entre 0 et 100.",
        },
        "volume": {
            "validate": "decimal",
            "criteria": ">=",
            "value": 0,
            "error_title": "Valeur invalide",
            "error_message": "Le volume doit être un nombre positif.",
        },
        "average_weighted_distance_km": {
            "validate": "decimal",
            "criteria": ">=",
            "value": 0,
            "error_title": "Valeur invalide",
            "error_message": "La distance moyenne doit être un nombre positif.",
        },
        "maximum_distance_km": {
            "validate": "decimal",
            "criteria": ">=",
            "value": 0,
            "error_title": "Valeur invalide",
            "error_message": "La distance maximale doit être un nombre positif.",
        },
    }

    for key, opts in validations.items():
        col_letter = COLUMN_BY_KEY[key]
        cell_range = f"{col_letter}{start_row}:{col_letter}{end_row}"
        sheet.data_validation(cell_range, opts)


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

    # Apply formats by key: decimal for ratio/volume, integer for distances
    col_format_by_key = {
        "dry_matter_ratio_percent": unlocked_decimal_number,
        "volume": unlocked_decimal_number,
        "average_weighted_distance_km": unlocked_number,
        "maximum_distance_km": unlocked_number,
    }
    for col_idx, (_, key) in enumerate(TABLE_HEADERS):
        fmt = col_format_by_key.get(key, unlocked)
        sheet.set_column(col_idx, col_idx, 25, fmt)


def _create_departments_sheet(workbook, bold, departments):
    """Create the Departments reference sheet."""
    sheet = workbook.add_worksheet("Departements")
    sheet.write(0, 0, "Code", bold)
    sheet.write(0, 1, "Nom", bold)

    for row, dept in enumerate(departments, start=1):
        sheet.write(row, 0, dept.code_dept)
        sheet.write(row, 1, f"{dept.code_dept} - {dept.name}")

    sheet.protect()


def _create_countries_sheet(workbook, bold, countries):
    """Create the Countries reference sheet."""
    sheet = workbook.add_worksheet("Pays")
    sheet.write(0, 0, "Code", bold)
    sheet.write(0, 1, "Nom", bold)

    for row, country in enumerate(countries, start=1):
        sheet.write(row, 0, country.code_pays)
        sheet.write(row, 1, country.name)

    sheet.protect()


def _create_inputs_sheet(workbook, bold, feedstocks):
    """Create the Feedstocks (Intrants) reference sheet."""
    sheet = workbook.add_worksheet("Intrants")
    sheet.write(0, 0, "Nom", bold)

    for row, input in enumerate(feedstocks, start=1):
        sheet.write(row, 0, input.name)

    sheet.protect()

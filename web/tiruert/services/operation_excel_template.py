from io import BufferedReader

import xlsxwriter

from core.models import Entity


def get_tiruert_operator_queryset():
    """Get queryset of entities authorized as operation recipients in TIRUERT."""
    return (
        Entity.objects.filter(
            is_enabled=True,
            entity_type=Entity.OPERATOR,
            is_tiruert_liable=True,
        )
        .exclude(accise_number__exact="")
        .order_by("name")
    )


TABLE_HEADERS = [
    ("Lot id", "lot_id"),
    ("Volume", "volume"),
    ("Type d'operation", "operation_type"),
    ("Destinataire", "credited_entity_name"),
    ("Destinataire id", "credited_entity"),
]

MAIN_SHEET_NAME = "Import d'opérations"
ENTITIES_SHEET_NAME = "Entités"
HEADER_ROW = 0
KEY_ROW = 1
FIRST_DATA_ROW = 2
LAST_DATA_ROW = 100001


def _excel_column_letter(col_index: int) -> str:
    """Return Excel column letter(s) for 0-based index (0=A, 25=Z, 26=AA, ...)."""
    if col_index < 26:
        return chr(65 + col_index)
    return _excel_column_letter(col_index // 26 - 1) + chr(65 + col_index % 26)


COLUMN_BY_KEY = {key: _excel_column_letter(i) for i, (_, key) in enumerate(TABLE_HEADERS)}


def create_operation_import_template() -> BufferedReader:
    location = "/tmp/tiruert_operations_import_template.xlsx"
    workbook = xlsxwriter.Workbook(location)

    header_format = workbook.add_format({"bold": True, "text_wrap": True, "valign": "vcenter"})
    unlocked_format = workbook.add_format({"locked": False})

    entities = list(get_tiruert_operator_queryset())

    _create_main_sheet(workbook, header_format, unlocked_format, entities)
    _create_entities_sheet(workbook, entities)

    workbook.close()
    return open(location, "rb")


def _create_main_sheet(workbook, header_format, unlocked_format, entities):
    sheet = workbook.add_worksheet(MAIN_SHEET_NAME)

    for col, (label, key) in enumerate(TABLE_HEADERS):
        sheet.write(HEADER_ROW, col, label, header_format)
        sheet.write(KEY_ROW, col, key)

    sheet.set_row(KEY_ROW, None, None, {"hidden": True})
    sheet.set_column(0, len(TABLE_HEADERS) - 2, 25, unlocked_format)
    sheet.set_column(len(TABLE_HEADERS) - 1, len(TABLE_HEADERS) - 1, None, None, {"hidden": True})
    sheet.protect(
        "",
        {
            "format_rows": False,
            "format_columns": False,
            "insert_rows": False,
            "delete_rows": False,
            "insert_columns": False,
            "delete_columns": False,
        },
    )

    _add_validations(sheet, entities)


def _add_validations(sheet, entities):
    start_row = FIRST_DATA_ROW + 1
    end_row = LAST_DATA_ROW + 1

    lot_id_col = COLUMN_BY_KEY["lot_id"]
    volume_col = COLUMN_BY_KEY["volume"]
    operation_type_col = COLUMN_BY_KEY["operation_type"]
    credited_entity_name_col = COLUMN_BY_KEY["credited_entity_name"]

    sheet.data_validation(
        f"{lot_id_col}{start_row}:{lot_id_col}{end_row}",
        {
            "validate": "integer",
            "criteria": ">=",
            "value": 1,
            "error_title": "Valeur invalide",
            "error_message": "Lot id doit etre un entier positif.",
        },
    )

    sheet.data_validation(
        f"{volume_col}{start_row}:{volume_col}{end_row}",
        {
            "validate": "decimal",
            "criteria": ">",
            "value": 0,
            "error_title": "Valeur invalide",
            "error_message": "Volume doit etre un nombre strictement positif.",
        },
    )

    sheet.data_validation(
        f"{operation_type_col}{start_row}:{operation_type_col}{end_row}",
        {
            "validate": "list",
            "source": ["TRANSFERT", "TENEUR"],
            "error_title": "Valeur invalide",
            "error_message": "Type d'operation doit etre TRANSFERT ou TENEUR.",
        },
    )

    if entities:
        entities_count = len(entities)
        source = f"={ENTITIES_SHEET_NAME}!$A$2:$A${entities_count + 1}"
        sheet.data_validation(
            f"{credited_entity_name_col}{start_row}:{credited_entity_name_col}{end_row}",
            {
                "validate": "list",
                "source": source,
                "ignore_blank": True,
                "input_title": "Destinataire",
                "input_message": "Renseigner uniquement pour TRANSFERT. Laisser vide pour TENEUR.",
                "error_title": "Valeur invalide",
                "error_message": "Destinataire doit etre un opérateur autorisé.",
            },
        )

        for row in range(FIRST_DATA_ROW, LAST_DATA_ROW + 1):
            excel_row = row + 1
            formula = (
                f'=IF({credited_entity_name_col}{excel_row}="","",'
                f"IFERROR(INDEX({ENTITIES_SHEET_NAME}!$B$2:$B${entities_count + 1},"
                f'MATCH({credited_entity_name_col}{excel_row},{ENTITIES_SHEET_NAME}!$A$2:$A${entities_count + 1},0)),""))'
            )
            sheet.write_formula(row, len(TABLE_HEADERS) - 1, formula)


def _create_entities_sheet(workbook, entities):
    sheet = workbook.add_worksheet(ENTITIES_SHEET_NAME)

    sheet.write(0, 0, "Destinataire")
    sheet.write(0, 1, "Id")

    for row, entity in enumerate(entities, start=1):
        sheet.write(row, 0, entity.name)
        sheet.write(row, 1, entity.id)

    sheet.protect()

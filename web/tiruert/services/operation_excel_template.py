from io import BufferedReader

import xlsxwriter
from django.db.models import Q

from core.models import CarbureLot, Entity
from tiruert.models import Operation
from tiruert.services.balance import BalanceService


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
    ("ID Carbure", "carbure_id"),
    ("Lot id", "lot_id"),
    ("Taux d'émission (gCO₂/MJ)", "emission_rate_per_mj"),
    ("Biocarburant", "biofuel"),
    ("Catégorie", "customs_category"),
    ("Matière première", "feedstock"),
    ("Volume disponible (L)", "available_volume"),
    ("Volume à prélever (L)", "volume"),
    ("Type d'opération", "operation_type"),
    ("Destinataire", "credited_entity_name"),
    ("Destinataire id", "credited_entity"),
]

MAIN_SHEET_NAME = "Import d'opérations"
ENTITIES_SHEET_NAME = "Entités"
HEADER_ROW = 0
KEY_ROW = 1
FIRST_DATA_ROW = 2
LAST_DATA_ROW = 10001


def _excel_column_letter(col_index: int) -> str:
    """Return Excel column letter(s) for 0-based index (0=A, 25=Z, 26=AA, ...)."""
    if col_index < 26:
        return chr(65 + col_index)
    return _excel_column_letter(col_index // 26 - 1) + chr(65 + col_index % 26)


COLUMN_BY_KEY = {key: _excel_column_letter(i) for i, (_, key) in enumerate(TABLE_HEADERS)}


def _get_operator_lots(entity_id: int) -> list[dict]:
    """Return lots attached to an operator with their available volume and metadata."""
    operations = Operation.objects.filter(Q(credited_entity_id=entity_id) | Q(debited_entity_id=entity_id))
    lot_balances = BalanceService.calculate_balance(
        operations=operations,
        entity_id=entity_id,
        group_by=BalanceService.GROUP_BY_LOT,
        unit="l",
    )

    lot_ids = [key[-1] for key in lot_balances.keys()]
    lot_metadata = {
        lot_id: (carbure_id or "", feedstock or "")
        for lot_id, carbure_id, feedstock in CarbureLot.objects.filter(id__in=lot_ids).values_list(
            "id", "carbure_id", "feedstock__name"
        )
    }

    lots = []
    for key, entry in lot_balances.items():
        # For GROUP_BY_LOT, key is (sector, customs_category, biofuel_code, lot_id)
        lot_id = key[-1]
        available_volume = round(float(entry.get("available_balance", 0) or 0), 2)
        if available_volume <= 0:
            continue

        carbure_id, feedstock = lot_metadata.get(lot_id, ("", ""))

        lots.append(
            {
                "lot_id": lot_id,
                "carbure_id": carbure_id,
                "available_volume": available_volume,
                "emission_rate_per_mj": float(entry.get("emission_rate_per_mj", 0) or 0),
                "biofuel": key[2],
                "customs_category": key[1],
                "feedstock": feedstock,
            }
        )

    lots.sort(key=lambda lot: lot["carbure_id"] or "")
    return lots


def create_operation_import_template(entity_id: int) -> BufferedReader:
    location = "/tmp/tiruert_operations_import_template.xlsx"
    workbook = xlsxwriter.Workbook(location)

    header_format = workbook.add_format({"bold": True, "text_wrap": True, "valign": "vcenter"})
    editable_format = workbook.add_format({"locked": False, "bg_color": "#FFF2CC"})
    decimal_format = workbook.add_format({"num_format": "0.00"})
    editable_decimal_format = workbook.add_format({"locked": False, "num_format": "0.00", "bg_color": "#FFF2CC"})

    entities = list(get_tiruert_operator_queryset())
    lots = _get_operator_lots(entity_id)

    _create_main_sheet(
        workbook,
        header_format,
        editable_format,
        editable_decimal_format,
        decimal_format,
        entities,
        lots,
    )
    _create_entities_sheet(workbook, entities)

    workbook.close()
    return open(location, "rb")


def _create_main_sheet(
    workbook,
    header_format,
    editable_format,
    editable_decimal_format,
    decimal_format,
    entities,
    lots,
):
    sheet = workbook.add_worksheet(MAIN_SHEET_NAME)

    for col, (label, key) in enumerate(TABLE_HEADERS):
        sheet.write(HEADER_ROW, col, label, header_format)
        sheet.write(KEY_ROW, col, key)

    sheet.set_row(KEY_ROW, None, None, {"hidden": True})
    sheet.set_column(0, 0, 25)
    sheet.set_column(1, 1, None, None, {"hidden": True})
    sheet.set_column(2, 2, 16, decimal_format)
    sheet.set_column(3, 4, 16)
    sheet.set_column(5, 5, 25)
    sheet.set_column(6, 6, 18, decimal_format)
    sheet.set_column(7, 7, 18, editable_decimal_format)
    sheet.set_column(8, 8, 20, editable_format)
    sheet.set_column(9, 9, 30, editable_format)
    sheet.set_column(len(TABLE_HEADERS) - 1, len(TABLE_HEADERS) - 1, None, None, {"hidden": True})

    for index, lot in enumerate(lots):
        row = FIRST_DATA_ROW + index
        sheet.write_string(row, 0, lot["carbure_id"])
        sheet.write_number(row, 1, lot["lot_id"])
        sheet.write_number(row, 2, lot["emission_rate_per_mj"])
        sheet.write_string(row, 3, lot["biofuel"])
        sheet.write_string(row, 4, lot["customs_category"])
        sheet.write_string(row, 5, lot["feedstock"])
        sheet.write_number(row, 6, lot["available_volume"], decimal_format)
        sheet.write_blank(row, 7, None, editable_decimal_format)

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
            "ignore_blank": True,
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
            "ignore_blank": True,
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

    sheet.set_column(1, 1, None, None, {"hidden": True})

    sheet.protect()
    sheet.hide()

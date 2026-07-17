from typing import Iterable

from core.excel import export_to_excel

from .columns import build_columns

SHEET_LABEL = "Plan d'approvisionnement"


def generate_supply_input_export(
    file_path: str,
    rows: Iterable[dict],
    *,
    dreal: bool,
):
    return export_to_excel(
        file_path,
        [
            {
                "label": SHEET_LABEL,
                "rows": rows,
                "columns": build_columns(dreal=dreal),
            }
        ],
        column_width=15,
    )

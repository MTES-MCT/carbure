import os
import tempfile
from datetime import datetime
from io import BufferedReader

import xlsxwriter

from biomethane.services.declaration_export import _format_value

from .columns import build_column_defs, section_formats
from .context import load_export_context


def generate_dreal_export(producer_ids, year: int) -> BufferedReader:
    """Generate a flat Excel file (one row per producer) of validated declarations for DREAL.

    Only producers within `producer_ids` that have a validated (DECLARED) declaration for `year`
    are exported.
    """
    filename = f"biomethane_dreal_export_{year}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    file_path = os.path.join(tempfile.gettempdir(), filename)

    columns = build_column_defs()
    export_context = load_export_context(producer_ids, year)

    workbook = xlsxwriter.Workbook(file_path)
    formats = section_formats(workbook)
    sheet = workbook.add_worksheet("Déclarations")

    sheet.set_column(0, len(columns) - 1, 30)
    for col_idx, column in enumerate(columns):
        sheet.write(0, col_idx, column.label, formats[column.section]["header"])

    for row_idx, declaration in enumerate(export_context.declarations, start=1):
        row_context = export_context.row_context(declaration)
        for col_idx, column in enumerate(columns):
            value = column.resolve(row_context)
            sheet.write(row_idx, col_idx, _format_value(value), formats[column.section]["cell"])

    workbook.close()
    return open(file_path, "rb")

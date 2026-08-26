from datetime import datetime
from io import BufferedReader

from core.excel_importer import ExcelImporter
from core.import_export_template import create_import_template
from traceability.handlers.action import ActionIndustryHandler


def build_action_import_template(handler: ActionIndustryHandler, entity=None) -> BufferedReader:
    columns = []
    for spec in handler.excel_columns:
        column = {"header": spec["header"]}
        options = spec.get("options")
        if callable(options):
            options = list(options(entity, handler))
        if options:
            column["options"] = options
        columns.append(column)

    return create_import_template(
        title=f"Import actions {handler.industry}",
        columns=columns,
    )


def parse_action_import_file(file, handler: ActionIndustryHandler) -> list[dict]:
    records = ExcelImporter.parse(file, header_row=0, sheet_name=f"Import actions {handler.industry}")
    header_to_key = {spec["header"]: spec["key"] for spec in handler.excel_columns if spec.get("key")}

    rows = []
    for record in records:
        row = {
            header_to_key[header]: value.date() if isinstance(value, datetime) else value
            for header, value in record.items()
            if header in header_to_key
        }
        if any(value not in (None, "") for value in row.values()):
            rows.append(row)
    return rows

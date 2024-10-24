from datetime import date, datetime
from io import BufferedReader
from typing import Any, Callable, Iterable, TypedDict

import pandas as pd
import xlsxwriter
from django.http import HttpResponse

from transactions.helpers import try_get_date


class Column(TypedDict):
    label: str
    value: str | Callable[[Any], str]


class SheetConfig(TypedDict):
    label: str
    rows: Iterable[Any]
    columns: Iterable[Column]


ExcelConfig = list[SheetConfig]


def export_to_excel(
    location: str, config: ExcelConfig, format: dict = None, column_width: int = 10, header_height: int = 20
):
    if format is None:
        format = {"bold": True}
    workbook = xlsxwriter.Workbook(location)

    bold_and_wrap_format = workbook.add_format(format)

    # each key in the config object will be turned into an excel sheet
    for sheet_config in config:
        label = sheet_config["label"]
        rows = sheet_config["rows"]
        columns = sheet_config["columns"]

        sheet = workbook.add_worksheet(label)
        sheet.set_row(0, header_height)
        sheet.set_column(0, len(columns), column_width)

        # create the sheet column headers
        for c, column in enumerate(columns):
            sheet.write(0, c, column["label"], bold_and_wrap_format)

        # fill the data inside the sheet
        for r, row in enumerate(rows):
            for c, column in enumerate(columns):
                value = get_value(column, row)
                sheet.write(r + 1, c, value)

    workbook.close()

    return open(location, "rb")


def ExcelResponse(file: BufferedReader):
    data = file.read()
    ctype = "application/vnd.ms-excel"
    response = HttpResponse(content=data, content_type=ctype)
    response["Content-Disposition"] = f'attachment; filename="{file.name.replace("/tmp/", "")}"'
    return response


# resolve the value for the given column and row
def get_value(column: Column, row: Any):
    column_value = column["value"]

    if callable(column_value):
        return column_value(row)
    else:
        return get_nested_value(row, column_value)


# access nested attributes following a certain path
def get_nested_value(obj: Any, path: str):
    current_obj = obj
    attributes = path.split(".")

    for attr in attributes:
        if current_obj is not None:
            if isinstance(current_obj, dict):
                current_obj = current_obj.get(attr, None)
            else:
                current_obj = getattr(current_obj, attr)

    if isinstance(current_obj, bool):
        return "OUI" if current_obj else "NON"

    if isinstance(current_obj, date) or isinstance(current_obj, datetime):
        return current_obj.strftime("%d/%m/%Y")

    if current_obj is None:
        return ""

    return current_obj


class TableParser:
    @staticmethod
    def parse_columns(df: pd.DataFrame, column_parsers: dict[str, Callable]):
        errors = []
        for i, row in df.iterrows():
            for column, parser in column_parsers.items():
                try:
                    df.at[i, column] = parser(row[column])
                except Exception:
                    errors.append({"row": i, "column": column})
        return df, errors

    @staticmethod
    def bool(cell):
        if isinstance(cell, str):
            cell = cell.lower()
        if cell == "oui" or cell == "yes" or cell == "x" or cell == 1 or cell is True or cell == "true":
            return True
        elif not cell or pd.isna(cell) or cell == "non" or cell == "no" or cell == "false":
            return False
        else:
            raise ValueError()

    @staticmethod
    def id(cell):
        try:
            return str(int(float(cell))).strip().upper()
        except Exception:
            return TableParser.str(cell).strip().upper()

    @staticmethod
    def int(cell):
        if not cell or pd.isna(cell):
            return 0
        else:
            return int(float(cell))

    @staticmethod
    def float(cell):
        if not cell or pd.isna(cell):
            return 0.0
        else:
            return round(float(cell), 2)

    @staticmethod
    def str(cell):
        if pd.isna(cell):
            return ""
        elif isinstance(cell, (str, int, float)):
            return str(cell).strip()
        else:
            raise ValueError()

    @staticmethod
    def date(cell):
        return try_get_date(cell)


def ExcelError(type: str, line: int, meta=None):
    error = {"line": int(line), "error": type}
    if meta is not None:
        error["meta"] = meta
    return error

import xlsxwriter
import pandas as pd
from io import BufferedReader
from django.http import HttpResponse
from typing import Any, Callable, Iterable, TypedDict
from transactions.helpers import try_get_date


class Column(TypedDict):
    label: str
    value: str | Callable[[Any], str]


class SheetConfig(TypedDict):
    label: str
    rows: Iterable[Any]
    columns: Iterable[Column]


ExcelConfig = list[SheetConfig]


def export_to_excel(location: str, config: ExcelConfig):
    workbook = xlsxwriter.Workbook(location)

    bold = workbook.add_format({"bold": True})

    # each key in the config object will be turned into an excel sheet
    for sheet_config in config:
        label = sheet_config["label"]
        rows = sheet_config["rows"]
        columns = sheet_config["columns"]

        sheet = workbook.add_worksheet(label)

        # create the sheet column headers
        for c, column in enumerate(columns):
            sheet.write(0, c, column["label"], bold)

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

    return current_obj


class TableParser:
    @staticmethod
    def parse_columns(df: pd.DataFrame, column_parsers: dict[str, Callable]):
        errors = []
        for i, row in df.iterrows():
            for column, parser in column_parsers.items():
                try:
                    df.at[i, column] = parser(row[column])
                except:
                    errors.append({"row": i, "column": column})
        return df, errors

    @staticmethod
    def bool(cell):
        if isinstance(cell, str):
            cell = cell.lower()
        if cell == "oui" or cell == "yes" or cell == "x" or cell == 1 or cell == True or cell == "true":
            return True
        elif not cell or pd.isna(cell) or cell == "non" or cell == "no" or cell == "false":
            return False
        else:
            raise ValueError()

    @staticmethod
    def id(cell):
        try:
            return str(int(float(cell))).upper()
        except:
            return TableParser.str(cell).upper()

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
            return str(cell)
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

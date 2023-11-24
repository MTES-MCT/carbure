from io import BufferedReader
from django.http import HttpResponse
import xlsxwriter
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
    response["Content-Disposition"] = f'attachment; filename="{file.name}"'
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


class ExcelParser:
    @staticmethod
    def bool(cell):
        return cell == "OUI" or cell == 1 or cell == True or cell == "true"

    @staticmethod
    def id(cell):
        try:
            return str(int(float(cell)))
        except:
            return str(cell)

    @staticmethod
    def float(cell):
        try:
            return round(float(cell), 2)
        except:
            return 0.0

    @staticmethod
    def str(cell):
        return str(cell)

    @staticmethod
    def date(cell):
        return try_get_date(cell)

from typing import List
from openpyxl import Workbook
from pyparsing import Any
from doublecount.parser.helpers import extract_year

from doublecount.parser.types import ProductionForecastRow, ProductionMaxRow, RequestedQuotaRow
from doublecount.parser.excel_to_carbure_convertor import get_biofuel_from_dc_biofuel, get_feedstock_from_dc_feedstock


def parse_production_max(excel_file: Workbook, start_year) -> List[ProductionMaxRow]:
    production_max_rows: List[ProductionMaxRow] = parse_production_data(
        excel_file=excel_file,
        sheet_name="Production",
        start_year=start_year,
        year_index=1,
        biofuel_index=2,
        feedstock_index=3,
        other_name="max_production_capacity",
        other_index=4,
    )
    return production_max_rows


def parse_production_forecast(excel_file: Workbook, start_year) -> List[ProductionForecastRow]:
    production_forecast_rows: List[ProductionForecastRow] = parse_production_data(
        excel_file=excel_file,
        sheet_name="Production",
        start_year=start_year,
        year_index=6,
        biofuel_index=7,
        feedstock_index=8,
        other_name="estimated_production",
        other_index=9,
    )
    return production_forecast_rows


def parse_requested_quota(excel_file: Workbook) -> List[RequestedQuotaRow]:
    requested_quota_rows: List[RequestedQuotaRow] = parse_production_data(
        excel_file=excel_file,
        sheet_name="Reconnaissance double comptage",
        start_year=0,
        year_index=1,
        biofuel_index=2,
        feedstock_index=3,
        other_name="requested_quota",
        other_index=4,
        other_required=True,
        other_alternative_index=10,  # outside of france production
    )

    return requested_quota_rows


def parse_production_data(
    excel_file: Workbook,
    sheet_name: str,
    start_year: int,
    year_index: int,
    feedstock_index: int,
    biofuel_index: int,
    other_name: str,  # column to get data like "max_production_capacity" or "estimated_production" or "requested_quota"
    other_index: int,  # index of the column in the excel file
    other_required: bool = False,  # if the other value is required
    other_alternative_index: int = None,  # alternative index of the other_column in the excel file to allow the first one is zero (ex : outside of france production)
) -> List[Any]:
    data_rows = []
    current_year = -1
    sheet = excel_file[sheet_name]
    for line, row in enumerate(sheet.iter_rows()):
        current_year = extract_year(row[year_index].value, current_year)
        if current_year < start_year:
            continue

        biofuel_name = None if "SOMME :" == row[biofuel_index].value else row[biofuel_index].value
        feedstock_name = row[feedstock_index].value
        elem_data = intOrZero(row[other_index].value)
        elem_alternative_data = 0
        if elem_data == 0 and other_alternative_index:  # outside of france production
            elem_alternative_data = intOrZero(row[other_alternative_index].value)

        other_column_empty = other_required and not (elem_data or elem_alternative_data)
        if current_year == -1 or other_column_empty or (not feedstock_name and not biofuel_name):
            continue

        feedstock = get_feedstock_from_dc_feedstock(feedstock_name)
        biofuel = get_biofuel_from_dc_biofuel(biofuel_name)

        production = {
            "line": line + 1,
            "year": current_year,
            "feedstock": feedstock,
            "biofuel": biofuel,
            other_name: elem_data,
        }

        data_rows.append(production)

    return data_rows


def intOrZero(value):
    try:
        return int(value)
    except:
        return 0

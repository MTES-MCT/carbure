import re
from typing import List
from openpyxl import Workbook
from core.models import MatierePremiere
from doublecount.parser.helpers import extract_year

from doublecount.parser.types import SourcingRow
from doublecount.parser.excel_to_carbure_convertor import DC_FEEDSTOCK_UNRECOGNIZED, get_feedstock_from_dc_feedstock


def parse_sourcing_forecast(excel_file: Workbook, start_year: int) -> List[SourcingRow]:
    sourcing_sheet = excel_file["Approvisionnement prévisionnel"]
    sourcing_rows: List[SourcingRow] = []
    dc_feedstocks = {f.code: f for f in MatierePremiere.objects.filter(is_double_compte=True)}

    current_year = -1

    for line, row in enumerate(sourcing_sheet.iter_rows()):
        current_year = extract_year(row[1].value, current_year)
        if current_year < start_year:
            continue

        feedstock_name = row[2].value
        origin_country_cell = row[3].value
        supply_country_cell = row[4].value
        transit_country_cell = row[5].value

        # skip row if no year or feedstock is defined
        # TO DELETE : if not feedstock_name or not origin_country_cell or feedstock_name == origin_country_cell:
        if not feedstock_name or feedstock_name == origin_country_cell:
            continue

        feedstock = get_feedstock_from_dc_feedstock(feedstock_name)

        # skip row if no feedstock is recognized and no origin country is defined
        if not feedstock and not origin_country_cell:
            continue

        # this allow to accept row without year but only when feedstock recognized
        if current_year == -1 and feedstock is None:
            continue

        origin_country = extract_country_code(origin_country_cell)
        supply_country = extract_country_code(supply_country_cell)
        transit_country = extract_country_code(transit_country_cell)

        sourcing: SourcingRow = {
            "line": line + 1,
            "year": current_year,
            "feedstock": feedstock,
            "origin_country": origin_country,
            "supply_country": supply_country,
            "transit_country": transit_country,
            "metric_tonnes": 0,
        }

        sourcing["metric_tonnes"] = row[6].value

        sourcing_rows.append(sourcing)

    return sourcing_rows


def extract_country_code(country_str: str) -> str | None:
    if country_str:
        return (country_str or "").split(" - ")[0].strip()
    else:
        return None

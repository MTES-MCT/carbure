import re
from typing import List, Tuple
from openpyxl import load_workbook
from doublecount.parser.parse_traceability import parse_traceability
from doublecount.parser.parse_info import parse_info
from doublecount.parser.parse_sourcing_forecast import parse_sourcing_forecast
from doublecount.parser.parse_production import parse_requested_quota, parse_production_max, parse_production_forecast

from doublecount.parser.types import ProductionForecastRow, ProductionMaxRow, RequestedQuotaRow, SourcingRow


def parse_dc_excel(
    filename: str,
) -> Tuple[dict[str], List[SourcingRow], List[ProductionMaxRow], List[ProductionForecastRow], List[RequestedQuotaRow]]:
    excel_file = load_workbook(filename, data_only=True)

    info = parse_info(excel_file)
    requested_quota_rows = parse_requested_quota(excel_file)

    years = [production_row["year"] for production_row in requested_quota_rows]
    start_year = max(years) - 1 if len(years) > 0 else info["start_year"] + 1 if info["start_year"] else 0

    tracability = parse_traceability(excel_file)
    sourcing_forecast_rows = parse_sourcing_forecast(excel_file, start_year=start_year)
    production_max_rows = parse_production_max(excel_file, start_year=start_year)
    production_forecast_rows = parse_production_forecast(excel_file, start_year=start_year)

    info["start_year"] = start_year
    return info, sourcing_forecast_rows, production_max_rows, production_forecast_rows, requested_quota_rows, tracability

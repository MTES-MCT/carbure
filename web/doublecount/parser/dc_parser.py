from typing import List, Tuple

from openpyxl import load_workbook

from doublecount.parser.parse_info import parse_info
from doublecount.parser.parse_production import parse_production_forecast, parse_production_max, parse_requested_quota
from doublecount.parser.parse_sourcing_forecast import parse_sourcing_forecast
from doublecount.parser.parse_sourcing_history import parse_sourcing_history
from doublecount.parser.types import (
    ProductionForecastRow,
    ProductionMaxRow,
    RequestedQuotaRow,
    SourcingHistoryRow,
    SourcingRow,
)


def parse_dc_excel(
    filename: str,
) -> Tuple[
    dict[str],
    List[SourcingRow],
    List[ProductionMaxRow],
    List[ProductionForecastRow],
    List[RequestedQuotaRow],
    List[SourcingHistoryRow],
    List[ProductionMaxRow],
    List[ProductionForecastRow],
]:
    excel_file = load_workbook(filename, data_only=True)

    info = parse_info(excel_file)
    requested_quota_rows = parse_requested_quota(excel_file)

    start_year = info.get("start_year")

    years = [production_row["year"] for production_row in requested_quota_rows]
    if not start_year and len(years) > 0:
        start_year = max(years) - 1

    # tracability = parse_traceability(excel_file)
    sourcing_forecast_rows = parse_sourcing_forecast(excel_file, start_year=start_year)
    production_max_rows = parse_production_max(excel_file, start_year=0)  # start_year=0 to get all production max rows
    production_forecast_rows = parse_production_forecast(excel_file, start_year=0)  # =0 to get all production rows
    sourcing_history_rows = parse_sourcing_history(excel_file, start_year=start_year)

    # Keep rows with year < start_year (history)
    production_max_history_rows = [row for row in production_max_rows if row["year"] < start_year]
    production_effective_history_rows = [row for row in production_forecast_rows if row["year"] < start_year]

    # Keep rows with year >= start_year
    production_max_rows = [row for row in production_max_rows if row["year"] >= start_year]
    production_forecast_rows = [row for row in production_forecast_rows if row["year"] >= start_year]

    info["start_year"] = start_year
    return (
        info,
        sourcing_forecast_rows,
        production_max_rows,
        production_forecast_rows,
        requested_quota_rows,
        sourcing_history_rows,
        production_max_history_rows,
        production_effective_history_rows,
    )

from datetime import date, timedelta
from typing import Optional, TypedDict
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Side, Border


class MeterReadingData(TypedDict):
    charge_point_id: str
    previous_reading: float
    current_reading: Optional[float]


def create_meter_reading_excel(quarter: int, year: int, meter_readings_data: list[MeterReadingData]):
    workbook = Workbook()
    sheet = workbook.active
    last_day = (date(year, quarter * 3, 1) + timedelta(days=31)).replace(day=1)

    # HEADER

    sheet["A1"] = "Identifiant du point de recharge communiqué à transport.data.gouv"
    sheet["B1"] = "Energie active totale soutirée lors du relevé précédent"
    sheet["C1"] = "Energie active totale soutirée au " + last_day.strftime("%d/%m/%Y")
    sheet["D1"] = "Electricité consommée sur la période"
    sheet["E1"] = "Electricité renouvelable consommée sur la période"

    sheet["G1"] = "Part renouvelable de l'électricité sur la période"
    sheet["G2"] = "24,92%"

    # BODY

    stations = set()
    renewable_part = 0.2492

    for i, reading in enumerate(meter_readings_data, 2):
        stations.add(reading.get("charge_point_id")[0:5])
        sheet[f"A{i}"] = reading["charge_point_id"]
        sheet[f"B{i}"] = reading["previous_reading"]
        sheet[f"C{i}"] = reading.get("current_reading") or ""
        sheet[f"D{i}"] = f"=IF(ISBLANK(C{i}), 0, C{i} - B{i})"
        sheet[f"E{i}"] = f"=IF(ISBLANK(D{i}), 0, ROUND(D{i} * {renewable_part}, 2))"

    # FOOTER

    last_reading_row = 1 + len(meter_readings_data)
    total_row = last_reading_row + 2
    sheet[f"A{total_row}"] = "Total"
    sheet[f"D{total_row}"] = f"=SUM(D2:D{total_row - 1})"
    sheet[f"E{total_row}"] = f"=SUM(E2:E{total_row - 1})"

    sheet[f"A{total_row + 2}"] = "Stations:"
    last_row = total_row + 2 + len(stations)
    for i, station in enumerate(stations, 1):
        sheet[f"A{total_row + 2 + i}"] = station

    # STYLING

    bold = Font(bold=True)
    side = Side(border_style="thin", color="AAAAAA")
    border = Border(top=side, left=side, right=side, bottom=side)
    yellow_bg = PatternFill(start_color="FFF2CC", fill_type="solid")
    blue_bg = PatternFill(start_color="D9E1F2", fill_type="solid")

    # header text
    for cell in sheet[1]:
        cell.font = bold
        cell.alignment = Alignment(wrapText=True)

    # row styles
    for i in range(1, last_row):
        sheet.row_dimensions[i].height = 48 if i == 1 else 16

        if i <= last_reading_row:
            sheet[f"A{i}"].fill = yellow_bg
            sheet[f"A{i}"].border = border
            sheet[f"B{i}"].fill = blue_bg
            sheet[f"B{i}"].border = border
            sheet[f"C{i}"].fill = blue_bg
            sheet[f"C{i}"].border = border

    # default column width
    for column in sheet.columns:
        sheet.column_dimensions[column[0].column_letter].width = 24

    # total row in bold
    sheet[total_row][0].font = bold
    sheet[total_row][3].font = bold
    sheet[total_row][4].font = bold

    # station header in bold
    sheet[f"A{total_row + 2}"].font = bold

    return workbook

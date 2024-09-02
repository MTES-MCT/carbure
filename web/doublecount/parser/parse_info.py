import traceback

from openpyxl import Workbook


def parse_info(excel_file: Workbook):
    try:
        presentation = excel_file["Présentation"]
        application = excel_file["Reconnaissance double comptage"]

        production_site = presentation[5][2].value
        producer_email = presentation[16][2].value
        try:
            # loop through reconaissance sheet to find the base year defined in it
            year_row_index = 0
            for i, row in enumerate(application.iter_rows()):
                year_row_index = i
                if row[6].value == "Première année de reconnaissance":
                    break
            start_year = int(application[year_row_index + 2][6].value)
        except Exception:
            start_year = 0

        return {
            "production_site": production_site,
            "producer_email": producer_email,
            "start_year": start_year,
        }
    except Exception:
        traceback.print_exc()
        return {"production_site": None, "producer_email": None, "start_year": 0}

import traceback
from openpyxl import Workbook


def parse_traceability(excel_file: Workbook):
    try:
        presentation = excel_file["Système de traçabilité"]

        before = presentation[5][1].value
        on_site = presentation[5][2].value
        after = presentation[5][3].value

        return {
            "before": before,
            "on_site": on_site,
            "after": after,
        }
    except:
        traceback.print_exc()
        return {
            "before": None,
            "on_site": None,
            "after": None,
        }

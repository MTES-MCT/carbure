import datetime
import os
from typing import List

import django
import openpyxl
import pandas as pd
from pandas._typing import Scalar

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import GenericCertificate
from core.utils import bulk_update_or_create

today = datetime.date.today()
CSV_FOLDER = os.environ["CARBURE_HOME"] + "/web/fixtures/csv/"


def get_sheet_data(sheet, convert_float: bool) -> List[List[Scalar]]:
    data: List[List[Scalar]] = []
    for row in sheet.rows:
        data.append([convert_cell(cell, convert_float) for cell in row])
    return data


def convert_cell(cell, convert_float: bool) -> Scalar:
    from openpyxl.cell.cell import TYPE_BOOL, TYPE_ERROR, TYPE_NUMERIC

    if cell.is_date:
        return cell.value
    elif cell.data_type == TYPE_ERROR:
        return np.nan
    elif cell.data_type == TYPE_BOOL:
        return bool(cell.value)
    elif cell.value is None:
        return ""  # compat with xlrd
    elif cell.data_type == TYPE_NUMERIC:
        # GH5394
        if convert_float:
            val = int(cell.value)
            if val == cell.value:
                return val
        else:
            return float(cell.value)

    return cell.value


def load_certificates():
    certificates = []
    filename = "%s/systeme_national.xlsx" % (CSV_FOLDER)
    wb = openpyxl.load_workbook(filename, data_only=True)
    sheet = wb.worksheets[0]
    data = get_sheet_data(sheet, convert_float=True)
    column_names = data[0]
    data = data[1:]
    df = pd.DataFrame(data, columns=column_names)
    df.fillna("", inplace=True)
    total_certs = len(df)
    # print(total_certs)
    # print(df)
    i = 0
    for row in df.iterrows():
        cert = row[1]
        # print(cert)
        # Nom                          CRISTAL UNION
        # Numéro SN                  SN_UN_2021_0115
        # Catégorie opérateur                      6
        # Fin de validité        2025-12-31 00:00:00
        # Name: 84, dtype: object
        valid_until = cert["Fin de validité"].date()

        certificates.append(
            {
                "certificate_id": cert["Numéro SN"],
                "certificate_type": GenericCertificate.SYSTEME_NATIONAL,
                "certificate_holder": cert["Nom"],
                "certificate_issuer": "DGEC",
                "address": "",
                "valid_from": datetime.date(2000, 1, 1),
                "valid_until": valid_until,
                "download_link": "",
                "scope": "%s" % (cert["Catégorie opérateur"]),
                "input": None,
                "output": None,
            }
        )
    try:
        existing, new = bulk_update_or_create(GenericCertificate, "certificate_id", certificates)
        print("[SN Certificates]: %d updated, %d created" % (len(existing), len(new)))
    except Exception as e:
        print("failed", e)
    return


def main():
    load_certificates()


if __name__ == "__main__":
    main()

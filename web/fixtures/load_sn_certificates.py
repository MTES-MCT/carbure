import sys, os
import django
import csv
import calendar
import datetime
import re
import argparse
import openpyxl
import pandas as pd
from typing import TYPE_CHECKING, Dict, List, Optional
from pandas._typing import FilePathOrBuffer, Scalar

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from certificates.models import SNCategory, SNCertificate, SNCertificateScope

today = datetime.date.today()
CSV_FOLDER = os.environ['CARBURE_HOME'] + '/web/fixtures/csv/'

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
    filename = '%s/systeme_national.xlsx' % (CSV_FOLDER)
    wb = openpyxl.load_workbook(filename, data_only=True)
    sheet = wb.worksheets[0]
    data = get_sheet_data(sheet, convert_float=True)
    column_names = data[0]
    data = data[1:]
    df = pd.DataFrame(data, columns=column_names)
    df.fillna('', inplace=True)
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
        valid_until = cert['Fin de validité'].date()
        d = {'certificate_holder': cert['Nom'],
             'valid_until': valid_until,
        }
        try:
            o, c = SNCertificate.objects.update_or_create(certificate_id=cert['Numéro SN'], defaults=d)
        except Exception as e:
            print('failed')
            print(e)

        # scopes
        scopes = str(cert['Catégorie opérateur']).split('&')
        for scope in scopes:
            scope = scope.strip()
            dbscope = SNCategory.objects.get(category_id=scope)
            SNCertificateScope.objects.update_or_create(certificate=o, scope=dbscope)
    return

def load_scopes():
    SCOPES = [('1', 'opérateurs qui produisent ou récoltent les matières premières dans leur état non transformé'),
              ('2', 'opérateurs qui collectent, stockent et commercialisent les matières premières dans leur état non transformé'),
              ('3', 'opérateurs qui transforment les matières premières et commercialisent les produits transformés intermédiaires'),
              ('4', 'opérateurs qui produisent et commercialisent les biocarburants et les bioliquides'),
              ('5', 'opérateurs qui mélangent des biocarburants et bioliquides entre eux et/ou commercialisent ces produits'),
              ('6', 'opérateurs qui incorporent ces produits pour produire des carburants ou des combustibles liquides au sens du code des douanes qu’ils mettent à la consommation'),
              ('6a', 'opérateurs qui incorporent ou font incorporer des biocarburants ou des bioliquides pour produire des carburants ou des combustibles liquides et/ou importent ou introduisent depuis un autre Etat membre des carburants ou des combustibles liquides contenant déjà des biocarburants ou des bioliquides, sans nécessairement les mettre eux-mêmes à la consommation'),
              ('6b', 'opérateurs qui ne font que mettre à la consommation des carburants ou des combustibles liquides, au sens du code des douanes, contenant des biocarburants ou des bioliquides')]
    for cat, description in SCOPES:
        SNCategory.objects.update_or_create(category_id=cat, defaults={'description': description})

        
def main():
    load_scopes()
    load_certificates()

if __name__ == '__main__':
    main()

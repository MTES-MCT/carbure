import sys, os
import django
import csv
import calendar
import datetime
import re
import argparse
from django.conf import settings
import openpyxl
import pandas as pd
from typing import TYPE_CHECKING, Dict, List, Optional
from pandas._typing import Scalar

from django.core.mail import send_mail
from django.db import transaction

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import GenericCertificate

today = datetime.date.today()
CSV_FOLDER = '/tmp/'

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
    new = []
    invalidated = []
    existing = {c.certificate_id: c for c in GenericCertificate.objects.filter(certificate_type=GenericCertificate.REDCERT)}

    filename = '%s/REDcert-certificates.xlsx' % (CSV_FOLDER)
    wb = openpyxl.load_workbook(filename, data_only=True)
    sheet = wb.worksheets[0]
    data = get_sheet_data(sheet, convert_float=True)
    column_names = data[0]
    data = data[1:]
    df = pd.DataFrame(data, columns=column_names)
    df.fillna('', inplace=True)
    total_certs = len(df)
    i = 0
    for row in df.iterrows():
        i += 1
        cert = row[1]
        #Identifier                            REDcert²-929-35291088
        #Name of the certificate holder               Quantafuel ASA
        #City                                                   Oslo
        #Post code                                               238
        #Country                                            Norwegen
        #Valid from                                       01.03.2021
        #Valid until                                      28.02.2022
        #Certified as                                        801,901
        #Certification body                       TÜV NORD CERT GmbH
        #Type                              Certificate REDcert² Chem
        #State                                                 Valid
        #Type of biomass
        valid_from = datetime.datetime.strptime(cert['Valid from'], "%d.%m.%Y").date()
        valid_until = datetime.datetime.strptime(cert['Valid until'], "%d.%m.%Y").date()
        if cert.Identifier in existing:
            # existing certificate, check if valid_until has changed
            existingcert = existing[cert.Identifier]
            if valid_until < existingcert.valid_until:
                print('Certificate %s %s invalidated' % (existingcert.certificate_id, existingcert.certificate_holder))
                print(valid_until, existingcert.valid_until)
                invalidated.append((cert, existingcert, existingcert.valid_until, valid_until))

        d = {
            'certificate_type': GenericCertificate.REDCERT,
            'certificate_holder': cert['Name of the certificate holder'],
            'certificate_issuer': cert['Certification body'],
            'address': '%s, %s, %s' % (cert['City'], cert['Post code'], cert['Country']),
            'valid_from': valid_from,
            'valid_until': valid_until,
            'scope': "%s" % (cert['Type']),
            'input': {'Type of biomass': cert['Type of biomass']},
            'output': None,
        }
        try:
            o, c = GenericCertificate.objects.update_or_create(certificate_id=cert['Identifier'], defaults=d)
            #print('Loaded %s' % (cert['Identifier']))
            if c == True:
                new.append(o)
        except Exception as e:
            print(e)
    return i, new, invalidated

def summary(args, nb_certificates, new_certificates, newly_invalidated_certificates):
    mail_content = "Hallo, <br />\n"
    mail_content += "Das Kärgement für zertificaten REDCert ist gut.<br />\n"
    mail_content += "%d zertificaten loaded<br />\n" % (nb_certificates)

    if len(new_certificates):
        mail_content += "Nouveaux certificats enregistrés:<br />\n"
        for nc in new_certificates:
            mail_content += '%s - %s' % (nc.certificate_type, nc.certificate_holder)
            mail_content += '<br />'

    fraud = False
    if len(newly_invalidated_certificates):
        for (nic, previous, prev_valid_date, new_valid_date) in newly_invalidated_certificates:
            fraud = True
            mail_content += "**** ACHTUNG certificat invalidé *****<br />"
            mail_content += '%s - %s' % (previous.certificate_id, previous.certificate_holder)
            mail_content += '<br />'
            mail_content += "Date de validité précédente: %s<br />" % (prev_valid_date)
            mail_content += "Nouvelle Date de validité: %s<br />" % (new_valid_date)
            mail_content += '<br />'

    subject = "Certificats REDCert"
    if fraud:
        subject += ' - ACHTUNG FRAUDE -'
        dst = ['carbure@beta.gouv.fr']
        send_mail(subject, mail_content, settings.DEFAULT_FROM_EMAIL, dst, fail_silently=False)
    else:
        print(mail_content)

def main(args):
    nb_certificates, new_certificates, newly_invalidated_certificates = load_certificates()
    summary(args, nb_certificates, new_certificates, newly_invalidated_certificates)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load REDCert certificates in database')
    parser.add_argument('--email', dest='email', action='store_true', default=False, help='Send a summary email')
    parser.add_argument('--test', dest='test', action='store_true', default=False, help='Send summary email to developers')
    args = parser.parse_args()
    main(args)

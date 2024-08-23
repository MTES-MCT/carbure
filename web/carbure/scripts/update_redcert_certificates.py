import argparse
import datetime
import os
from typing import List, Tuple, cast

import django
import numpy as np
import openpyxl
import pandas as pd
import requests
from django.conf import settings
from django.core.mail import get_connection, send_mail
from openpyxl.cell.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet
from pandas._typing import Scalar

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import GenericCertificate
from core.utils import bulk_update_or_create

today = datetime.date.today()
REDCERT_CERT_PAGE = "https://redcert.eu/ZertifikateDatenAnzeige.aspx"
REDCERT_EXPORT_URL = "https://redcert.eu/ExportZertifikate.aspx"
DESTINATION_FOLDER = "/tmp/"
REDCERT_ENGLISH_PARAMS = {"__EVENTTARGET": "ctl00$languageEnglishLinkButton"}


def update_redcert_certificates(email: bool = False, test: bool = False) -> None:
    download_redcert_certificates()
    nb_certificates, new_certificates, newly_invalidated_certificates = save_redcert_certificates()
    send_email_summary(nb_certificates, new_certificates, newly_invalidated_certificates, email)


def download_redcert_certificates() -> None:
    session = requests.Session()
    # first, load the page showing the list of redcert certs -> it sets a session cookie
    print("Initializing connection to redcert servers...")
    session.get(REDCERT_CERT_PAGE)
    session.post(REDCERT_CERT_PAGE, data=REDCERT_ENGLISH_PARAMS)  # switch to english
    # now we can try to download the actual xlsx file
    print("Downloading the list of certificates...")
    res = session.get(REDCERT_EXPORT_URL, allow_redirects=True)
    filename = "%s/REDcert-certificates.xlsx" % (DESTINATION_FOLDER)
    open(filename, "wb").write(res.content)
    print("File was created successfully.")


def save_redcert_certificates() -> Tuple[int, list, list]:
    certificates = []
    invalidated = []
    existing = {c.certificate_id: c for c in GenericCertificate.objects.filter(certificate_type=GenericCertificate.REDCERT)}  # fmt: skip

    filename = "%s/REDcert-certificates.xlsx" % (DESTINATION_FOLDER)
    wb = openpyxl.load_workbook(filename, data_only=True)
    sheet = wb.worksheets[0]
    data = get_sheet_data(sheet, convert_float=True)
    column_names = data[0]
    data = data[1:]
    df = pd.DataFrame(data, columns=column_names)
    df.fillna("", inplace=True)
    i = 0
    for row in df.iterrows():
        i += 1
        cert = row[1]
        # Identifier                            REDcert²-929-35291088
        # Name of the certificate holder               Quantafuel ASA
        # City                                                   Oslo
        # Post code                                               238
        # Country                                            Norwegen
        # Valid from                                       01.03.2021
        # Valid until                                      28.02.2022
        # Certified as                                        801,901
        # Certification body                       TÜV NORD CERT GmbH
        # Type                              Certificate REDcert² Chem
        # State                                                 Valid
        # Type of biomass
        valid_from = datetime.datetime.strptime(cert["Valid from"], "%d.%m.%Y").date()
        valid_until = datetime.datetime.strptime(cert["Valid until"], "%d.%m.%Y").date()
        if cert.Identifier in existing:
            # existing certificate, check if valid_until has changed
            existingcert = existing[cert.Identifier]
            if valid_until < existingcert.valid_until:
                print("Certificate %s %s invalidated" % (existingcert.certificate_id, existingcert.certificate_holder))
                print(valid_until, existingcert.valid_until)
                invalidated.append((cert, existingcert, existingcert.valid_until, valid_until))

        certificates.append(
            {
                "certificate_id": cert["Identifier"],
                "certificate_type": GenericCertificate.REDCERT,
                "certificate_holder": cert["Name of the certificate holder"],
                "certificate_issuer": cert["Certification body"],
                "address": "%s, %s, %s" % (cert["City"], cert["Post code"], cert["Country"]),
                "valid_from": valid_from,
                "valid_until": valid_until,
                "scope": "%s" % (cert["Type"]),
                "input": {"Type of biomass": cert["Type of biomass"]},
                "output": None,
            }
        )

    existing, new = bulk_update_or_create(GenericCertificate, "certificate_id", certificates)
    print("[REDcert Certificates] %d updated, %d created" % (len(existing), len(new)))
    return i, new, invalidated


def send_email_summary(
    nb_certificates: int,
    new_certificates: list,
    newly_invalidated_certificates: list,
    email: bool,
) -> None:
    mail_content = "Bonjour, <br />\n"
    mail_content += "La mise à jour des certificats REDcert s'est bien passée.<br />\n"
    mail_content += "%d certificats vérifiés<br />\n" % (nb_certificates)

    if len(new_certificates):
        mail_content += "%d nouveaux certificats enregistrés :<br />\n" % len(new_certificates)
        for nc in new_certificates:
            mail_content += "%s - %s" % (nc.certificate_type, nc.certificate_holder)
            mail_content += "<br />"

    fraud = False
    if len(newly_invalidated_certificates):
        for (_, previous, prev_valid_date, new_valid_date) in newly_invalidated_certificates:
            fraud = True
            mail_content += "**** Certificat expiré *****<br />"
            mail_content += "%s - %s" % (previous.certificate_id, previous.certificate_holder)
            mail_content += "<br />"
            mail_content += "Date de validité précédente: %s<br />" % (prev_valid_date)
            mail_content += "Nouvelle Date de validité: %s<br />" % (new_valid_date)
            mail_content += "<br />"

    try:
        connection = get_connection()
        connection.open()
        if email and fraud:
            send_mail(
                "Certificats REDcert",
                mail_content,
                settings.DEFAULT_FROM_EMAIL,
                ["carbure@beta.gouv.fr"],
                fail_silently=False,
                connection=connection,
            )
        else:
            print(mail_content)
        connection.close()
    except Exception:
        print("Error: Could not open connection to email backend")
        return


def get_sheet_data(sheet: Worksheet, convert_float: bool) -> List[List[Scalar]]:
    data: List[List[Scalar]] = []
    for row in sheet.rows:
        data.append([convert_cell(cell, convert_float) for cell in row])
    return data


def convert_cell(cell: Cell, convert_float: bool) -> Scalar:
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
            val = int(cast(float, cell.value))
            if val == cell.value:
                return val
        else:
            return float(cast(float, cell.value))

    return cell.value


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load REDCert certificates in database")
    parser.add_argument("--email", dest="email", action="store_true", default=False, help="Send a summary email")
    parser.add_argument("--test", dest="test", action="store_true", default=False, help="Send email to developers")
    args = parser.parse_args()
    update_redcert_certificates(args.email, args.test)
